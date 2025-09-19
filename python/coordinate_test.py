#!/usr/bin/env python3
"""
Test to verify Tobii coordinate system mapping
"""

import pygame
import socket
import time
import pandas as pd
import numpy as np

class CoordinateTest:
    def __init__(self, width=1920, height=1080):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Eye Tracking Coordinate Test")
        self.clock = pygame.time.Clock()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        
        # Test positions (in normalized coordinates)
        self.test_positions = [
            (0.0, 0.0, "Top-Left"),
            (0.5, 0.0, "Top-Center"),
            (1.0, 0.0, "Top-Right"),
            (0.0, 0.5, "Middle-Left"),
            (0.5, 0.5, "Center"),
            (1.0, 0.5, "Middle-Right"),
            (0.0, 1.0, "Bottom-Left"),
            (0.5, 1.0, "Bottom-Center"),
            (1.0, 1.0, "Bottom-Right")
        ]
        
    def send_command(self, command, host='127.0.0.1', port=1234):
        """Send command to Tobii program"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(command.encode(), (host, port))
            sock.close()
            return True
        except:
            return False
    
    def pixel_to_normalized(self, pixel_x, pixel_y):
        """Convert pixel coordinates to normalized coordinates"""
        norm_x = pixel_x / self.width
        norm_y = pixel_y / self.height
        return norm_x, norm_y
    
    def normalized_to_pixel(self, norm_x, norm_y):
        """Convert normalized coordinates to pixel coordinates"""
        pixel_x = int(norm_x * self.width)
        pixel_y = int(norm_y * self.height)
        return pixel_x, pixel_y
    
    def run_coordinate_test(self):
        """Run the coordinate mapping test"""
        print("=== Tobii Coordinate System Test ===")
        print("Look at each RED dot when it appears")
        print("Press SPACE to start collecting data for that position")
        print("Press ESCAPE to exit")
        print("=====================================")
        
        results = []
        font = pygame.font.Font(None, 36)
        
        for norm_x, norm_y, position_name in self.test_positions:
            print(f"\nTesting position: {position_name} ({norm_x}, {norm_y})")
            
            # Convert to pixel coordinates
            pixel_x, pixel_y = self.normalized_to_pixel(norm_x, norm_y)
            
            # Display the target
            running = True
            collecting = False
            start_time = None
            
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return results
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return results
                        elif event.key == pygame.K_SPACE:
                            if not collecting:
                                print("  Collecting gaze data for 3 seconds...")
                                self.send_command('c')  # Start continuous recording
                                collecting = True
                                start_time = time.time()
                
                # Clear screen
                self.screen.fill(self.BLACK)
                
                # Draw target dot
                pygame.draw.circle(self.screen, self.RED, (pixel_x, pixel_y), 15)
                
                # Draw crosshair at target
                pygame.draw.line(self.screen, self.WHITE, 
                               (pixel_x-20, pixel_y), (pixel_x+20, pixel_y), 2)
                pygame.draw.line(self.screen, self.WHITE, 
                               (pixel_x, pixel_y-20), (pixel_x, pixel_y+20), 2)
                
                # Show instructions
                if not collecting:
                    text = font.render(f"Look at RED dot ({position_name})", True, self.WHITE)
                    instruction = font.render("Press SPACE to collect data", True, self.GREEN)
                else:
                    elapsed = time.time() - start_time
                    text = font.render(f"Collecting... {3-elapsed:.1f}s", True, self.GREEN)
                    instruction = font.render("Keep looking at the dot!", True, self.GREEN)
                
                self.screen.blit(text, (10, 10))
                self.screen.blit(instruction, (10, 50))
                
                # Show expected coordinates
                coord_text = font.render(f"Expected: ({norm_x:.1f}, {norm_y:.1f})", True, self.BLUE)
                self.screen.blit(coord_text, (10, self.height - 40))
                
                pygame.display.flip()
                self.clock.tick(60)
                
                # Check if collection time is up
                if collecting and time.time() - start_time >= 3:
                    self.send_command('s')  # Stop recording
                    collecting = False
                    
                    # Analyze the data
                    time.sleep(0.5)  # Wait for data to be written
                    gaze_data = self.analyze_position_data(norm_x, norm_y, position_name)
                    if gaze_data:
                        results.append(gaze_data)
                    
                    running = False  # Move to next position
        
        return results
    
    def analyze_position_data(self, expected_x, expected_y, position_name):
        """Analyze gaze data for a specific position"""
        try:
            data = pd.read_csv('../data/gaze_data.txt', sep='\t', header=None,
                             names=['timestamp', 'x', 'y'])
            
            if len(data) < 10:  # Need at least some samples
                print("  Not enough data collected")
                return None
            
            # Get recent data (last 3 seconds worth)
            recent_data = data.tail(100)  # Approximate
            
            mean_x = recent_data['x'].mean()
            mean_y = recent_data['y'].mean()
            std_x = recent_data['x'].std()
            std_y = recent_data['y'].std()
            
            error_x = abs(mean_x - expected_x)
            error_y = abs(mean_y - expected_y)
            
            print(f"  Expected: ({expected_x:.3f}, {expected_y:.3f})")
            print(f"  Measured: ({mean_x:.3f}, {mean_y:.3f})")
            print(f"  Error: ({error_x:.3f}, {error_y:.3f})")
            print(f"  Std Dev: ({std_x:.3f}, {std_y:.3f})")
            
            return {
                'position': position_name,
                'expected_x': expected_x,
                'expected_y': expected_y,
                'measured_x': mean_x,
                'measured_y': mean_y,
                'error_x': error_x,
                'error_y': error_y,
                'std_x': std_x,
                'std_y': std_y
            }
            
        except Exception as e:
            print(f"  Error analyzing data: {e}")
            return None
    
    def print_summary(self, results):
        """Print test summary"""
        if not results:
            print("No results collected")
            return
            
        print("\n=== COORDINATE TEST SUMMARY ===")
        print(f"{'Position':<15} {'Expected':<12} {'Measured':<12} {'Error':<10}")
        print("-" * 55)
        
        total_error_x = 0
        total_error_y = 0
        
        for r in results:
            print(f"{r['position']:<15} "
                  f"({r['expected_x']:.1f},{r['expected_y']:.1f})<6 "
                  f"({r['measured_x']:.2f},{r['measured_y']:.2f})<6 "
                  f"({r['error_x']:.3f},{r['error_y']:.3f})")
            total_error_x += r['error_x']
            total_error_y += r['error_y']
        
        avg_error_x = total_error_x / len(results)
        avg_error_y = total_error_y / len(results)
        
        print(f"\nAverage Error: ({avg_error_x:.3f}, {avg_error_y:.3f})")
        
        # Interpretation
        print("\n=== INTERPRETATION ===")
        if avg_error_x < 0.05 and avg_error_y < 0.05:
            print("✓ Excellent calibration accuracy")
        elif avg_error_x < 0.1 and avg_error_y < 0.1:
            print("✓ Good calibration accuracy")
        else:
            print("⚠ Calibration may need improvement")
            
        print(f"Coordinate system confirmed:")
        print(f"- (0,0) = Top-left corner")
        print(f"- (1,1) = Bottom-right corner") 
        print(f"- Values outside 0-1 range indicate gaze beyond screen edges")

def main():
    tester = CoordinateTest()
    results = tester.run_coordinate_test()
    tester.print_summary(results)
    pygame.quit()

if __name__ == "__main__":
    main()