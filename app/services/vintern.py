import os
import numpy as np
import torch
import torchvision.transforms as T
from PIL import Image
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoModel, AutoTokenizer
import logging
import psutil
import gc

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
MODEL_NAME = "5CD-AI/Vintern-1B-v3_5"
MODEL_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model-image")

logger = logging.getLogger(__name__)


class VinternAIService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize basic attributes but don't load model yet
            cls._instance._initialized = False
            cls._instance._ensure_model_cache_dir()
            cls._instance.device = None
            cls._instance.model = None
            cls._instance.tokenizer = None
            cls._instance.generation_config = None
        return cls._instance

    def _should_use_lightweight_mode(self):
        """Determine if we should use lightweight mode based on available memory"""
        try:
            if self.device.type == "cuda":
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                return gpu_memory < 6  # Use lightweight mode if less than 6GB GPU memory
            else:
                available_ram = psutil.virtual_memory().available / (1024**3)  # GB
                return available_ram < 8  # Use lightweight mode if less than 8GB RAM
        except:
            return True  # Default to lightweight mode if we can't check

    def _get_generation_config(self):
        """Get generation config based on mode"""
        if self.lightweight_mode:
            logger.info("Using lightweight mode for better stability")
            return dict(
                max_new_tokens=512,  # Very short responses
                do_sample=False, 
                num_beams=1,  # No beam search
                repetition_penalty=1.0,  # No repetition penalty
                temperature=0.7,  # Add some randomness
                top_p=0.9  # Nucleus sampling
            )
        else:
            logger.info("Using standard mode for better quality")
            return dict(
                max_new_tokens=1024,  # Reduced from 2048 for speed
                do_sample=False, 
                num_beams=1,  # Reduced from 3 for speed
                repetition_penalty=1.1  # Reduced from 1.2
            )

    def _monitor_memory(self):
        """Monitor memory usage and warn if getting low"""
        try:
            if self.device.type == "cuda":
                allocated = torch.cuda.memory_allocated(0) / (1024**3)  # GB
                reserved = torch.cuda.memory_reserved(0) / (1024**3)  # GB
                if allocated > 6:  # Warning if using more than 6GB
                    logger.warning(f"High GPU memory usage: {allocated:.1f}GB allocated, {reserved:.1f}GB reserved")
                    return False
            else:
                available_ram = psutil.virtual_memory().available / (1024**3)  # GB
                if available_ram < 2:  # Warning if less than 2GB available
                    logger.warning(f"Low RAM available: {available_ram:.1f}GB")
                    return False
            return True
        except:
            return True  # Assume OK if we can't check

    def _check_system_resources(self):
        """Check if system has enough resources to load the model"""
        try:
            # Check available RAM
            available_ram = psutil.virtual_memory().available / (1024**3)  # GB
            if available_ram < 4:  # Need at least 4GB free RAM
                logger.warning(f"Low RAM available: {available_ram:.1f}GB. Model may be slow or crash.")
            
            # Check GPU memory if using CUDA
            if self.device.type == "cuda":
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                logger.info(f"GPU memory: {gpu_memory:.1f}GB")
                
                # Check available GPU memory
                torch.cuda.empty_cache()
                free_gpu_memory = torch.cuda.memory_reserved(0) / (1024**3)  # GB
                logger.info(f"Free GPU memory: {free_gpu_memory:.1f}GB")
                
        except Exception as e:
            logger.warning(f"Could not check system resources: {e}")

    def _get_device(self):
        """Detect and return the best available device"""
        try:
            # Force CUDA initialization
            if torch.cuda.is_available():
                # Try to create a small tensor to ensure CUDA is working
                test_tensor = torch.randn(1, 1).cuda()
                del test_tensor
                torch.cuda.empty_cache()
                
                device = torch.device("cuda")
                logger.info(f"CUDA is available. Using GPU: {torch.cuda.get_device_name()}")
                logger.info(f"CUDA version: {torch.version.cuda}")
                logger.info(f"PyTorch version: {torch.__version__}")
                return device
            else:
                logger.warning("torch.cuda.is_available() returned False")
                device = torch.device("cpu")
                logger.info("CUDA not available. Using CPU")
                return device
        except Exception as e:
            logger.error(f"Error during CUDA detection: {e}")
            logger.info("Falling back to CPU")
            return torch.device("cpu")

    def _ensure_initialized(self):
        """Lazy initialization - only load model when actually needed"""
        if not self._initialized:
            logger.info("Starting VinternAIService initialization...")
            
            # Detect available device
            self.device = self._get_device()
            logger.info(f"Selected device: {self.device}")
            
            # Check system resources before loading
            self._check_system_resources()
            
            # Set lightweight mode based on available memory
            self.lightweight_mode = self._should_use_lightweight_mode()
            
            # Load model and tokenizer only once
            logger.info("Loading model...")
            model = self._load_model()
            logger.info("Loading tokenizer...")
            tokenizer = self._load_tokenizer()
            
            self.tokenizer = tokenizer
            self.model = model
            self.generation_config = self._get_generation_config()
            self._initialized = True
            logger.info("VinternAIService initialized successfully")
            
            # Verify device after initialization
            if self.device.type == "cuda":
                try:
                    model_device = next(self.model.parameters()).device
                    logger.info(f"Model loaded on device: {model_device}")
                    if model_device.type == "cuda":
                        logger.info("✅ Model successfully loaded on GPU!")
                    else:
                        logger.warning("⚠️ Model loaded but not on GPU!")
                except Exception as e:
                    logger.error(f"Error checking model device: {e}")

    def _ensure_model_cache_dir(self):
        """Ensure the model cache directory exists"""
        os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
        logger.info(f"Model cache directory: {MODEL_CACHE_DIR}")

    def _load_model(self):
        """Load the model from local cache or download if not available"""
        model_path = os.path.join(MODEL_CACHE_DIR, "vintern-model")
        
        if os.path.exists(model_path):
            logger.info("Loading model from local cache...")
            try:
                model = AutoModel.from_pretrained(
                    model_path,
                    torch_dtype=torch.bfloat16,
                    low_cpu_mem_usage=True,
                    trust_remote_code=True,
                    use_flash_attn=False,
                ).eval().to(self.device)
                logger.info("Model loaded successfully from local cache")
                return model
            except Exception as e:
                logger.warning(f"Failed to load model from cache: {e}. Downloading fresh copy...")
                # Remove corrupted cache
                import shutil
                if os.path.exists(model_path):
                    shutil.rmtree(model_path)
        
        # Download model if not in cache
        logger.info("Downloading model...")
        model = AutoModel.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            use_flash_attn=False,
            cache_dir=MODEL_CACHE_DIR
        ).eval().to(self.device)
        
        # Save model to local cache
        logger.info("Saving model to local cache...")
        model.save_pretrained(model_path)
        logger.info("Model saved to local cache successfully")
        
        return model

    def _load_tokenizer(self):
        """Load the tokenizer from local cache or download if not available"""
        tokenizer_path = os.path.join(MODEL_CACHE_DIR, "vintern-tokenizer")
        
        if os.path.exists(tokenizer_path):
            logger.info("Loading tokenizer from local cache...")
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    tokenizer_path, 
                    trust_remote_code=True, 
                    use_fast=False
                )
                logger.info("Tokenizer loaded successfully from local cache")
                return tokenizer
            except Exception as e:
                logger.warning(f"Failed to load tokenizer from cache: {e}. Downloading fresh copy...")
                # Remove corrupted cache
                import shutil
                if os.path.exists(tokenizer_path):
                    shutil.rmtree(tokenizer_path)
        
        # Download tokenizer if not in cache
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, 
            trust_remote_code=True, 
            use_fast=False,
            cache_dir=MODEL_CACHE_DIR
        )
        
        # Save tokenizer to local cache
        logger.info("Saving tokenizer to local cache...")
        tokenizer.save_pretrained(tokenizer_path)
        logger.info("Tokenizer saved to local cache successfully")
        
        return tokenizer

    def build_transform(self, input_size):
        MEAN, STD = IMAGENET_MEAN, IMAGENET_STD
        transform = T.Compose([
            T.Lambda(lambda img: img.convert('RGB') if img.mode != 'RGB' else img),
            T.Resize((input_size, input_size), interpolation=InterpolationMode.BICUBIC),
            T.ToTensor(),
            T.Normalize(mean=MEAN, std=STD)
        ])
        return transform

    def find_closest_aspect_ratio(self, aspect_ratio, target_ratios, width, height, image_size):
        best_ratio_diff = float('inf')
        best_ratio = (1, 1)
        area = width * height
        for ratio in target_ratios:
            target_aspect_ratio = ratio[0] / ratio[1]
            ratio_diff = abs(aspect_ratio - target_aspect_ratio)
            if ratio_diff < best_ratio_diff:
                best_ratio_diff = ratio_diff
                best_ratio = ratio
            elif ratio_diff == best_ratio_diff:
                if area > 0.5 * image_size * image_size * ratio[0] * ratio[1]:
                    best_ratio = ratio
        return best_ratio

    def dynamic_preprocess(self, image, min_num=1, max_num=12, image_size=448, use_thumbnail=False):
        orig_width, orig_height = image.size
        aspect_ratio = orig_width / orig_height

        # calculate the existing image aspect ratio
        target_ratios = set(
            (i, j) for n in range(min_num, max_num + 1) for i in range(1, n + 1) for j in range(1, n + 1) if
            i * j <= max_num and i * j >= min_num)
        target_ratios = sorted(target_ratios, key=lambda x: x[0] * x[1])

        # find the closest aspect ratio to the target
        target_aspect_ratio = self.find_closest_aspect_ratio(
            aspect_ratio, target_ratios, orig_width, orig_height, image_size)

        # calculate the target width and height
        target_width = image_size * target_aspect_ratio[0]
        target_height = image_size * target_aspect_ratio[1]
        blocks = target_aspect_ratio[0] * target_aspect_ratio[1]

        # resize the image
        resized_img = image.resize((target_width, target_height))
        processed_images = []
        for i in range(blocks):
            box = (
                (i % (target_width // image_size)) * image_size,
                (i // (target_width // image_size)) * image_size,
                ((i % (target_width // image_size)) + 1) * image_size,
                ((i // (target_width // image_size)) + 1) * image_size
            )
            # split the image
            split_img = resized_img.crop(box)
            processed_images.append(split_img)
        assert len(processed_images) == blocks
        if use_thumbnail and len(processed_images) != 1:
            thumbnail_img = image.resize((image_size, image_size))
            processed_images.append(thumbnail_img)
        return processed_images

    def load_image(self, image_file, input_size=448, max_num=12):
        image = Image.open(image_file).convert('RGB')
        transform = self.build_transform(input_size=input_size)
        images = self.dynamic_preprocess(image, image_size=input_size, use_thumbnail=True, max_num=max_num)
        pixel_values = [transform(image) for image in images]
        pixel_values = torch.stack(pixel_values)
        return pixel_values

    def generate_input(self, image_file: str):
        # Ensure service is initialized
        self._ensure_initialized()
        
        try:
            # Clear memory before processing
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            
            pixel_values = self.load_image(image_file, max_num=6).to(torch.bfloat16).to(self.device)
            return pixel_values
        except Exception as e:
            logger.error(f"Error generating input: {e}")
            raise

    def generate_chat(self, pixel_values, prompt):
        # Ensure service is initialized
        
        try:
            # Clear memory before generation
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            
            response = self.model.chat(self.tokenizer, pixel_values, prompt, self.generation_config)
            
            # Clear memory after generation
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            
            return response
        except Exception as e:
            logger.error(f"Error generating chat: {e}")
            # Clear memory on error
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
            gc.collect()
            raise

    def force_cuda_reinit(self):
        """Force CUDA re-initialization"""
        try:
            if torch.cuda.is_available():
                # Clear any existing CUDA state
                torch.cuda.empty_cache()
                
                # Force CUDA initialization with a test tensor
                test_tensor = torch.randn(1, 1).cuda()
                result = test_tensor.cuda().sum().item()
                del test_tensor
                torch.cuda.empty_cache()
                
                logger.info(f"CUDA re-initialization successful. Test result: {result}")
                return True
            else:
                logger.warning("CUDA not available for re-initialization")
                return False
        except Exception as e:
            logger.error(f"CUDA re-initialization failed: {e}")
            return False

    def check_gpu_usage(self):
        """Check if GPU is being used and show memory usage"""
        # Ensure service is initialized
        self._ensure_initialized()
        
        try:
            if self.device.type == "cuda":
                # Check if model is on GPU
                model_device = next(self.model.parameters()).device
                is_on_gpu = model_device.type == "cuda"
                
                # Get GPU memory info
                allocated = torch.cuda.memory_allocated(0) / (1024**3)  # GB
                reserved = torch.cuda.memory_reserved(0) / (1024**3)  # GB
                total = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # GB
                
                return {
                    "device": "cuda",
                    "model_on_gpu": is_on_gpu,
                    "gpu_name": torch.cuda.get_device_name(0),
                    "memory_allocated_gb": round(allocated, 2),
                    "memory_reserved_gb": round(reserved, 2),
                    "total_gpu_memory_gb": round(total, 2),
                    "free_gpu_memory_gb": round(total - allocated, 2),
                    "utilization_percent": round((allocated / total) * 100, 1),
                    "cuda_available": torch.cuda.is_available(),
                    "torch_version": torch.__version__,
                    "cuda_version": torch.version.cuda
                }
            else:
                return {
                    "device": "cpu",
                    "model_on_gpu": False,
                    "message": "CUDA not available",
                    "cuda_available": torch.cuda.is_available(),
                    "torch_version": torch.__version__,
                    "cuda_version": torch.version.cuda if hasattr(torch.version, 'cuda') else "N/A"
                }
        except Exception as e:
            return {"error": str(e)}

    def verify_gpu_usage(self):
        """Verify that tensors and model are actually on GPU"""
        # Ensure service is initialized
        self._ensure_initialized()
        
        try:
            if self.device.type == "cuda":
                # Check model device
                model_device = next(self.model.parameters()).device
                model_on_gpu = model_device.type == "cuda"
                
                # Check if we can create a test tensor on GPU
                test_tensor = torch.randn(1, 1).to(self.device)
                tensor_on_gpu = test_tensor.device.type == "cuda"
                
                # Clean up test tensor
                del test_tensor
                torch.cuda.empty_cache()
                
                return {
                    "model_on_gpu": model_on_gpu,
                    "tensor_on_gpu": tensor_on_gpu,
                    "cuda_available": torch.cuda.is_available(),
                    "current_device": str(self.device),
                    "model_device": str(model_device)
                }
            else:
                return {"device": "cpu", "cuda_available": False}
        except Exception as e:
            return {"error": str(e)}

vintern_ai_service = VinternAIService()