"""
Network Drive Performance Test for Promethean Light Server Viability
Tests read/write speeds, latency, and SQLite performance on network location.
"""

import os
import time
import sqlite3
import tempfile
import shutil
from pathlib import Path
import random
import string

# Test configuration
import sys
TEST_DIR = sys.argv[1] if len(sys.argv) > 1 else r"V:\mel_energy_office\Business Dev\promethean_test"
TEST_SIZES = {
    "large_file": 100 * 1024 * 1024,  # 100 MB
    "small_files": 1024,  # 1 KB each
    "num_small_files": 100
}

class NetworkPerformanceTester:
    def __init__(self, test_dir):
        self.test_dir = Path(test_dir)
        self.results = {}

    def setup(self):
        """Create test directory"""
        print(f"Setting up test directory: {self.test_dir}")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        print("[OK] Test directory created")

    def cleanup(self):
        """Remove test directory and files"""
        print("\nCleaning up test files...")
        try:
            shutil.rmtree(self.test_dir)
            print("[OK] Cleanup complete")
        except Exception as e:
            print(f"[WARNING] Cleanup warning: {e}")

    def test_sequential_write(self):
        """Test large file sequential write speed"""
        print("\n" + "="*60)
        print("TEST 1: Sequential Write Speed (100 MB file)")
        print("="*60)

        test_file = self.test_dir / "write_test.bin"
        size = TEST_SIZES["large_file"]
        data = os.urandom(size)

        start = time.time()
        with open(test_file, 'wb') as f:
            f.write(data)
        elapsed = time.time() - start

        speed_mbps = (size / 1024 / 1024) / elapsed
        self.results['sequential_write'] = {
            'time': elapsed,
            'speed_mbps': speed_mbps
        }

        print(f"  Write time: {elapsed:.2f} seconds")
        print(f"  Write speed: {speed_mbps:.2f} MB/s")
        print(f"  Status: {'[GOOD] GOOD' if speed_mbps > 10 else '[SLOW] SLOW' if speed_mbps > 5 else '[POOR] POOR'}")

        return test_file

    def test_sequential_read(self, test_file):
        """Test large file sequential read speed"""
        print("\n" + "="*60)
        print("TEST 2: Sequential Read Speed (100 MB file)")
        print("="*60)

        start = time.time()
        with open(test_file, 'rb') as f:
            data = f.read()
        elapsed = time.time() - start

        size = len(data)
        speed_mbps = (size / 1024 / 1024) / elapsed
        self.results['sequential_read'] = {
            'time': elapsed,
            'speed_mbps': speed_mbps
        }

        print(f"  Read time: {elapsed:.2f} seconds")
        print(f"  Read speed: {speed_mbps:.2f} MB/s")
        print(f"  Status: {'[GOOD] GOOD' if speed_mbps > 20 else '[SLOW] SLOW' if speed_mbps > 10 else '[POOR] POOR'}")

    def test_small_file_operations(self):
        """Test many small file operations (typical for HTML serving)"""
        print("\n" + "="*60)
        print("TEST 3: Small File Operations (100 x 1KB files)")
        print("="*60)

        small_dir = self.test_dir / "small_files"
        small_dir.mkdir(exist_ok=True)

        # Write test
        print("\n  Writing 100 small files...")
        data = ''.join(random.choices(string.ascii_letters, k=TEST_SIZES["small_files"]))
        start = time.time()
        for i in range(TEST_SIZES["num_small_files"]):
            file_path = small_dir / f"file_{i}.txt"
            with open(file_path, 'w') as f:
                f.write(data)
        write_elapsed = time.time() - start

        # Read test
        print("  Reading 100 small files...")
        start = time.time()
        for i in range(TEST_SIZES["num_small_files"]):
            file_path = small_dir / f"file_{i}.txt"
            with open(file_path, 'r') as f:
                _ = f.read()
        read_elapsed = time.time() - start

        self.results['small_files'] = {
            'write_time': write_elapsed,
            'read_time': read_elapsed,
            'write_files_per_sec': TEST_SIZES["num_small_files"] / write_elapsed,
            'read_files_per_sec': TEST_SIZES["num_small_files"] / read_elapsed
        }

        print(f"\n  Write: {write_elapsed:.2f}s ({self.results['small_files']['write_files_per_sec']:.1f} files/s)")
        print(f"  Read: {read_elapsed:.2f}s ({self.results['small_files']['read_files_per_sec']:.1f} files/s)")
        print(f"  Status: {'[GOOD] GOOD' if read_elapsed < 5 else '[SLOW] SLOW' if read_elapsed < 10 else '[POOR] POOR'}")

    def test_sqlite_performance(self):
        """Test SQLite database operations (critical for Promethean Light)"""
        print("\n" + "="*60)
        print("TEST 4: SQLite Database Performance")
        print("="*60)

        db_path = self.test_dir / "test.db"

        # Create and write
        print("\n  Creating database and inserting 1000 records...")
        start = time.time()
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY,
                content TEXT,
                metadata TEXT,
                embedding BLOB
            )
        ''')

        # Insert test data
        test_data = []
        for i in range(1000):
            content = f"Test document {i} " * 50  # ~1KB per record
            metadata = '{"source": "test", "timestamp": "2024-01-01"}'
            embedding = os.urandom(768 * 4)  # Simulated 768-dim float32 embedding
            test_data.append((i, content, metadata, embedding))

        cursor.executemany('INSERT INTO documents VALUES (?, ?, ?, ?)', test_data)
        conn.commit()
        write_elapsed = time.time() - start

        # Query test
        print("  Running 100 queries...")
        start = time.time()
        for i in range(100):
            cursor.execute('SELECT * FROM documents WHERE id = ?', (random.randint(0, 999),))
            _ = cursor.fetchone()
        query_elapsed = time.time() - start

        # Full scan test
        print("  Running full table scan...")
        start = time.time()
        cursor.execute('SELECT COUNT(*) FROM documents')
        _ = cursor.fetchone()
        scan_elapsed = time.time() - start

        conn.close()

        self.results['sqlite'] = {
            'write_time': write_elapsed,
            'query_time': query_elapsed,
            'scan_time': scan_elapsed,
            'queries_per_sec': 100 / query_elapsed
        }

        print(f"\n  Insert 1000 records: {write_elapsed:.2f}s")
        print(f"  100 queries: {query_elapsed:.2f}s ({self.results['sqlite']['queries_per_sec']:.1f} queries/s)")
        print(f"  Full scan: {scan_elapsed:.2f}s")
        print(f"  Status: {'[GOOD] GOOD' if query_elapsed < 1 else '[SLOW] SLOW' if query_elapsed < 3 else '[POOR] POOR'}")

    def test_latency(self):
        """Test basic file operation latency"""
        print("\n" + "="*60)
        print("TEST 5: File Operation Latency")
        print("="*60)

        test_file = self.test_dir / "latency_test.txt"

        # Measure create latency
        latencies = []
        for i in range(20):
            start = time.time()
            with open(test_file, 'w') as f:
                f.write("test")
            latencies.append((time.time() - start) * 1000)  # Convert to ms
            test_file.unlink()

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        self.results['latency'] = {
            'avg_ms': avg_latency,
            'max_ms': max_latency,
            'min_ms': min_latency
        }

        print(f"\n  Average latency: {avg_latency:.1f} ms")
        print(f"  Min latency: {min_latency:.1f} ms")
        print(f"  Max latency: {max_latency:.1f} ms")
        print(f"  Status: {'[GOOD] GOOD' if avg_latency < 50 else '[SLOW] SLOW' if avg_latency < 100 else '[POOR] POOR'}")

    def print_summary(self):
        """Print comprehensive summary and recommendations"""
        print("\n" + "="*60)
        print("SUMMARY & RECOMMENDATIONS")
        print("="*60)

        # Calculate overall viability score
        scores = []

        # Sequential write
        write_speed = self.results['sequential_write']['speed_mbps']
        if write_speed > 10:
            scores.append(('Sequential Write', 'GOOD', '[GOOD]'))
        elif write_speed > 5:
            scores.append(('Sequential Write', 'ACCEPTABLE', '[SLOW]'))
        else:
            scores.append(('Sequential Write', 'POOR', '[POOR]'))

        # Sequential read
        read_speed = self.results['sequential_read']['speed_mbps']
        if read_speed > 20:
            scores.append(('Sequential Read', 'GOOD', '[GOOD]'))
        elif read_speed > 10:
            scores.append(('Sequential Read', 'ACCEPTABLE', '[SLOW]'))
        else:
            scores.append(('Sequential Read', 'POOR', '[POOR]'))

        # Small files (critical for HTML serving)
        read_time = self.results['small_files']['read_time']
        if read_time < 5:
            scores.append(('HTML File Serving', 'GOOD', '[GOOD]'))
        elif read_time < 10:
            scores.append(('HTML File Serving', 'ACCEPTABLE', '[SLOW]'))
        else:
            scores.append(('HTML File Serving', 'POOR', '[POOR]'))

        # SQLite (critical for Promethean Light)
        query_time = self.results['sqlite']['query_time']
        if query_time < 1:
            scores.append(('SQLite Queries', 'GOOD', '[GOOD]'))
        elif query_time < 3:
            scores.append(('SQLite Queries', 'ACCEPTABLE', '[SLOW]'))
        else:
            scores.append(('SQLite Queries', 'POOR', '[POOR]'))

        # Latency
        latency = self.results['latency']['avg_ms']
        if latency < 50:
            scores.append(('Network Latency', 'GOOD', '[GOOD]'))
        elif latency < 100:
            scores.append(('Network Latency', 'ACCEPTABLE', '[SLOW]'))
        else:
            scores.append(('Network Latency', 'POOR', '[POOR]'))

        print("\nPerformance Assessment:")
        print("-" * 60)
        for metric, status, symbol in scores:
            print(f"  {symbol} {metric:25s} {status}")

        # Count good/acceptable/poor
        good_count = sum(1 for _, status, _ in scores if status == 'GOOD')
        acceptable_count = sum(1 for _, status, _ in scores if status == 'ACCEPTABLE')
        poor_count = sum(1 for _, status, _ in scores if status == 'POOR')

        print("\n" + "="*60)
        print("FINAL RECOMMENDATION")
        print("="*60)

        if good_count >= 4:
            print("\n[GOOD] RECOMMENDED: This network location is SUITABLE for hosting")
            print("  Promethean Light server for your team.")
            print("\n  Recommended setup:")
            print("  • FastAPI server on V: drive")
            print("  • Serve HTML/JSON data via HTTP")
            print("  • SQLite database on V: drive (with read-only replicas)")
            print("  • Team accesses via http://server:port")
        elif acceptable_count + good_count >= 4:
            print("\n[SLOW] CONDITIONAL: This location is MARGINALLY ACCEPTABLE")
            print("  Performance is adequate but not optimal.")
            print("\n  Recommendations:")
            print("  • Use for read-only HTML/data serving")
            print("  • Keep SQLite database local, sync periodically")
            print("  • Use caching heavily (Redis/in-memory)")
            print("  • Consider static HTML export instead of live server")
        else:
            print("\n[POOR] NOT RECOMMENDED: This location is TOO SLOW")
            print("  Network performance is insufficient for server hosting.")
            print("\n  Alternative approaches:")
            print("  • Host server on local machine, VPN access for team")
            print("  • Export static HTML reports, copy to V: drive")
            print("  • Use cloud hosting (AWS/Azure) with better network")
            print("  • Set up dedicated local server with proper networking")

        print("\n" + "="*60)
        print("DETAILED METRICS")
        print("="*60)
        print(f"\nSequential Write: {self.results['sequential_write']['speed_mbps']:.2f} MB/s")
        print(f"Sequential Read: {self.results['sequential_read']['speed_mbps']:.2f} MB/s")
        print(f"Small File Read: {self.results['small_files']['read_files_per_sec']:.1f} files/s")
        print(f"SQLite Queries: {self.results['sqlite']['queries_per_sec']:.1f} queries/s")
        print(f"Average Latency: {self.results['latency']['avg_ms']:.1f} ms")

        return good_count >= 4

def main():
    print("="*60)
    print("DRIVE PERFORMANCE TEST")
    print(f"Testing: {TEST_DIR}")
    print("="*60)

    tester = NetworkPerformanceTester(TEST_DIR)

    try:
        tester.setup()

        # Run all tests
        test_file = tester.test_sequential_write()
        tester.test_sequential_read(test_file)
        tester.test_small_file_operations()
        tester.test_sqlite_performance()
        tester.test_latency()

        # Print summary
        viable = tester.print_summary()

    except Exception as e:
        print(f"\n[POOR] ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.cleanup()

    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

if __name__ == "__main__":
    main()
