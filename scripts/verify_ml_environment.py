import sys
import os
import torch
import torchvision

def verify():
    print("=" * 60)
    print("MarineShield Environment Verification")
    print("=" * 60)
    
    # 1. Python version
    python_ver = sys.version
    print(f"Python Version: {python_ver}")
    
    # 2. Active virtual environment
    virtual_env = os.environ.get('VIRTUAL_ENV', None)
    is_in_venv = sys.prefix != sys.base_prefix
    print(f"Active Virtual Environment: {virtual_env if virtual_env else 'None'}")
    print(f"Running within Virtual Environment: {is_in_venv} (sys.prefix: {sys.prefix})")
    
    # 3. PyTorch version
    pytorch_ver = torch.__version__
    print(f"PyTorch Version: {pytorch_ver}")
    
    # 4. torchvision version
    torchvision_ver = torchvision.__version__
    print(f"torchvision Version: {torchvision_ver}")
    
    # 5. CUDA availability
    cuda_avail = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_avail}")
    
    if not cuda_avail:
        print("[-] Verification FAILED: CUDA is not available.")
        sys.exit(1)
        
    # 6. GPU model
    gpu_name = torch.cuda.get_device_name(0)
    print(f"GPU Model: {gpu_name}")
    
    # 7. GPU memory
    device_properties = torch.cuda.get_device_properties(0)
    total_memory_gb = device_properties.total_memory / (1024 ** 3)
    print(f"GPU Total Memory: {total_memory_gb:.2f} GB")
    
    # 8. Basic CUDA tensor allocation
    try:
        print("Allocating basic CUDA tensor...")
        tensor_a = torch.ones((1000, 1000), device='cuda')
        print(f"[+] CUDA tensor allocated successfully: {tensor_a.shape} on {tensor_a.device}")
    except Exception as e:
        print(f"[-] Verification FAILED: CUDA tensor allocation failed: {e}")
        sys.exit(1)
        
    # 9. Basic GPU matrix multiplication
    try:
        print("Performing basic GPU matrix multiplication...")
        tensor_b = torch.randn((1000, 1000), device='cuda')
        result = torch.matmul(tensor_a, tensor_b)
        expected_sum = result.sum().item()
        print(f"[+] GPU Matrix multiplication completed successfully. Result sum: {expected_sum:.4f}")
    except Exception as e:
        print(f"[-] Verification FAILED: GPU matrix multiplication failed: {e}")
        sys.exit(1)
        
    print("=" * 60)
    print("[+] SUCCESS: All environment verification checks passed!")
    print("=" * 60)

if __name__ == "__main__":
    verify()
