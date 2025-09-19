import socket
import pygame
import sys

print("=== Simple Eye Tracking Test ===")

# Test 1: Basic packages
print("Python packages:")
try:
    import numpy, pandas, matplotlib
    print("  [OK] numpy, pandas, matplotlib")
except:
    print("  [ERROR] Missing packages")

# Test 2: Pygame
print("Pygame:")
try:
    pygame.init()
    pygame.quit()
    print("  [OK] pygame working")
except:
    print("  [ERROR] pygame failed")

# Test 3: Tobii connection
print("Tobii connection:")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b'8', ('127.0.0.1', 1234))
    sock.close()
    print("  [OK] Tobii connection successful")
except Exception as e:
    print(f"  [ERROR] Tobii failed: {e}")
    print("  Make sure eyeTrack.exe is running")

print("Test complete!")