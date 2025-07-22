import serial
import serial.tools.list_ports
import time
import threading
import statistics
import hashlib

def find_arduino():
    """Find Arduino port automatically"""
    ports = list(serial.tools.list_ports.comports())
    
    print("Available ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")
    
    # Look for common Arduino identifiers
    arduino_keywords = ['arduino', 'ch340', 'ch341', 'ftdi', 'usb serial']
    
    for port in ports:
        desc = (port.description or "").lower()
        mfg = (port.manufacturer or "").lower()
        
        if any(keyword in desc or keyword in mfg for keyword in arduino_keywords):
            print(f"Found Arduino: {port.device}")
            return port.device
    
    # Fallback: return first available port
    if ports:
        print(f"Using first available port: {ports[0].device}")
        return ports[0].device
    
    return None

class PacketOptimizer:
    def __init__(self, port):
        self.port = port
        self.arduino = None
        self.BAUD_RATE = 2000000  # Fixed at 2M baud as specified
        
        # Test results
        self.test_results = {}
        
    def connect(self):
        """Connect to Arduino at 2M baud"""
        try:
            if self.arduino and self.arduino.is_open:
                self.arduino.close()
            
            self.arduino = serial.Serial(self.port, self.BAUD_RATE, timeout=1.0)
            time.sleep(2)  # Give Arduino time to initialize
            
            # Clear any initial data
            if self.arduino.in_waiting > 0:
                self.arduino.read(self.arduino.in_waiting)
            
            print(f"Connected to {self.port} at {self.BAUD_RATE:,} baud")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def create_test_packet(self, size, packet_id):
        """Create a test packet with verification data"""
        if size < 10:
            size = 10  # Minimum size for packet ID and basic data
        
        # Format: [ID:4chars][DATA][CHECKSUM:4chars]\n
        header = f"{packet_id:04d}"
        
        # Calculate how much data we need (total - header - checksum - newline)
        data_size = size - 4 - 4 - 1  # 4 for ID, 4 for checksum, 1 for newline
        if data_size < 1:
            data_size = 1
        
        # Create predictable data pattern
        data = ''.join([chr(65 + (i % 26)) for i in range(data_size)])  # A-Z pattern
        
        # Create checksum of header + data
        content = header + data
        checksum = hashlib.md5(content.encode()).hexdigest()[:4].upper()
        
        packet = f"{header}{data}{checksum}\n"
        return packet
    
    def verify_packet(self, sent_packet, received_packet):
        """Verify received packet matches sent packet"""
        sent_clean = sent_packet.strip()
        received_clean = received_packet.strip()
        
        if sent_clean == received_clean:
            return True, "Perfect match"
        
        if len(received_clean) == 0:
            return False, "No response"
        
        if len(received_clean) != len(sent_clean):
            return False, f"Length mismatch: sent {len(sent_clean)}, got {len(received_clean)}"
        
        # Check for partial corruption
        differences = sum(1 for a, b in zip(sent_clean, received_clean) if a != b)
        corruption_pct = (differences / len(sent_clean)) * 100
        
        return False, f"{differences} corrupted chars ({corruption_pct:.1f}%)"
    
    def test_packet_size(self, packet_size, num_packets=50, delay_between_ms=0):
        """Test specific packet size with timing and verification"""
        print(f"\nTesting {packet_size}-byte packets (delay: {delay_between_ms}ms)...")
        
        results = {
            'packet_size': packet_size,
            'num_packets': num_packets,
            'delay_ms': delay_between_ms,
            'round_trip_times': [],
            'verification_results': [],
            'success_count': 0,
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'corruption_count': 0,
            'timeout_count': 0,
            'partial_count': 0
        }
        
        for packet_id in range(num_packets):
            try:
                # Clear buffer before test
                if self.arduino.in_waiting > 0:
                    junk = self.arduino.read(self.arduino.in_waiting)
                    if len(junk) > 0:
                        print(f"  Cleared {len(junk)} bytes of leftover data")
                
                # Create test packet
                test_packet = self.create_test_packet(packet_size, packet_id)
                
                # Send packet and measure timing
                start_time = time.time()
                self.arduino.write(test_packet.encode())
                self.arduino.flush()
                
                results['total_bytes_sent'] += len(test_packet)
                
                # Wait for complete echo with timeout
                received_data = ""
                timeout_start = time.time()
                expected_length = len(test_packet)
                
                while len(received_data) < expected_length and (time.time() - timeout_start) < 3.0:
                    if self.arduino.in_waiting > 0:
                        chunk = self.arduino.read(self.arduino.in_waiting).decode('utf-8', errors='ignore')
                        received_data += chunk
                    else:
                        time.sleep(0.01)  # Small delay if no data available
                
                end_time = time.time()
                round_trip_ms = (end_time - start_time) * 1000
                results['round_trip_times'].append(round_trip_ms)
                results['total_bytes_received'] += len(received_data)
                
                # Verify the packet
                is_valid, error_msg = self.verify_packet(test_packet, received_data)
                results['verification_results'].append((is_valid, error_msg))
                
                if is_valid:
                    results['success_count'] += 1
                    status = "✓"
                elif "timeout" in error_msg.lower() or "no response" in error_msg.lower():
                    results['timeout_count'] += 1
                    status = "T"
                elif "length mismatch" in error_msg.lower():
                    results['partial_count'] += 1
                    status = "P"
                else:
                    results['corruption_count'] += 1
                    status = "C"
                
                print(f"  Packet {packet_id+1:3d}: {status} {round_trip_ms:6.1f}ms - {error_msg}")
                
                # Optional delay between packets
                if delay_between_ms > 0:
                    time.sleep(delay_between_ms / 1000.0)
                
            except Exception as e:
                print(f"  Packet {packet_id+1:3d}: ✗ Exception: {e}")
                results['verification_results'].append((False, f"Exception: {e}"))
        
        # Calculate statistics
        if results['round_trip_times']:
            results['avg_round_trip_ms'] = statistics.mean(results['round_trip_times'])
            results['min_round_trip_ms'] = min(results['round_trip_times'])
            results['max_round_trip_ms'] = max(results['round_trip_times'])
            results['stddev_round_trip_ms'] = statistics.stdev(results['round_trip_times']) if len(results['round_trip_times']) > 1 else 0
        else:
            results['avg_round_trip_ms'] = 0
            results['min_round_trip_ms'] = 0
            results['max_round_trip_ms'] = 0
            results['stddev_round_trip_ms'] = 0
        
        results['success_rate'] = (results['success_count'] / num_packets) * 100
        results['effective_throughput_bps'] = (results['total_bytes_sent'] * 2) / (sum(results['round_trip_times']) / 1000) if results['round_trip_times'] else 0
        
        # Print summary for this packet size
        print(f"  Results: {results['success_rate']:.1f}% success, {results['avg_round_trip_ms']:.1f}ms avg")
        print(f"    Timeouts: {results['timeout_count']}, Partial: {results['partial_count']}, Corrupted: {results['corruption_count']}")
        print(f"    Effective throughput: {results['effective_throughput_bps']:.0f} bytes/sec")
        
        return results
    
    def run_optimization(self):
        """Run packet size optimization tests"""
        if not self.connect():
            return None
        
        print("Arduino Packet Size and Timing Optimization")
        print("=" * 60)
        print(f"Fixed baud rate: {self.BAUD_RATE:,}")
        print(f"Testing port: {self.port}")
        
        # Test different packet sizes
        packet_sizes = list(range(63, 64))
        delays = [0, 1, 2, 3, 5, 10, 15, 25, 33, 47, 56]  # Different delays between packets
        
        all_results = []
        
        for delay in delays:
            print(f"\n{'='*60}")
            print(f"Testing with {delay}ms delay between packets")
            print(f"{'='*60}")
            
            for packet_size in packet_sizes:
                try:
                    result = self.test_packet_size(packet_size, num_packets=256, delay_between_ms=delay)
                    if result:
                        all_results.append(result)
                    
                except KeyboardInterrupt:
                    print("\nOptimization interrupted by user")
                    break
                except Exception as e:
                    print(f"Error testing {packet_size} bytes: {e}")
            
            if KeyboardInterrupt:
                break
        
        # Clean up
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        
        self.print_optimization_summary(all_results)
        return all_results
    
    def print_optimization_summary(self, results):
        """Print optimization summary and recommendations"""
        print(f"\n{'='*100}")
        print("PACKET OPTIMIZATION SUMMARY")
        print(f"{'='*100}")
        
        if not results:
            print("No successful tests!")
            return
        
        # Group results by delay
        delay_groups = {}
        for result in results:
            delay = result['delay_ms']
            if delay not in delay_groups:
                delay_groups[delay] = []
            delay_groups[delay].append(result)
        
        for delay, group_results in delay_groups.items():
            print(f"\n--- Results with {delay}ms delay ---")
            print(f"{'Size':<6} {'Success%':<9} {'Avg RT(ms)':<12} {'Throughput(B/s)':<15} {'T/P/C':<8}")
            print("-" * 60)
            
            # Sort by success rate, then by throughput
            sorted_results = sorted(group_results, key=lambda x: (x['success_rate'], x['effective_throughput_bps']), reverse=True)
            
            for result in sorted_results:
                size = result['packet_size']
                success = result['success_rate']
                avg_rt = result['avg_round_trip_ms']
                throughput = result['effective_throughput_bps']
                errors = f"{result['timeout_count']}/{result['partial_count']}/{result['corruption_count']}"
                
                print(f"{size:<6} {success:>7.1f}% {avg_rt:>10.1f} {throughput:>13.0f} {errors:<8}")
        
        # Overall recommendations
        print(f"\n{'='*100}")
        print("RECOMMENDATIONS:")
        
        # Find best overall (highest success rate with good throughput)
        reliable_results = [r for r in results if r['success_rate'] >= 95.0]
        
        if reliable_results:
            best_reliable = max(reliable_results, key=lambda x: x['effective_throughput_bps'])
            print(f"🏆 Best Reliable: {best_reliable['packet_size']} bytes, {best_reliable['delay_ms']}ms delay")
            print(f"    ({best_reliable['success_rate']:.1f}% success, {best_reliable['effective_throughput_bps']:.0f} B/s)")
        
        # Find fastest (lowest latency) with good reliability
        fast_reliable = [r for r in reliable_results if r['avg_round_trip_ms'] > 0]
        if fast_reliable:
            fastest = min(fast_reliable, key=lambda x: x['avg_round_trip_ms'])
            print(f"⚡ Lowest Latency: {fastest['packet_size']} bytes, {fastest['delay_ms']}ms delay")
            print(f"    ({fastest['avg_round_trip_ms']:.1f}ms avg, {fastest['success_rate']:.1f}% success)")
        
        # Find highest throughput overall
        if results:
            max_throughput = max(results, key=lambda x: x['effective_throughput_bps'])
            print(f"📊 Max Throughput: {max_throughput['packet_size']} bytes, {max_throughput['delay_ms']}ms delay")
            print(f"    ({max_throughput['effective_throughput_bps']:.0f} B/s, {max_throughput['success_rate']:.1f}% success)")

def main():
    port = find_arduino()
    if not port:
        print("No serial ports found!")
        return
    
    try:
        optimizer = PacketOptimizer(port)
        optimizer.run_optimization()
        
    except KeyboardInterrupt:
        print("\nOptimization stopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()