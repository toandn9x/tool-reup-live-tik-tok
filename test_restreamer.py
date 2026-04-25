import unittest
from unittest.mock import patch, MagicMock
import subprocess
from tiktok_restreamer import TikTokRestreamer
import os

class TestTikTokRestreamer(unittest.TestCase):

    def setUp(self):
        self.tiktok_urls = ["https://www.tiktok.com/@test/live", "https://www.tiktok.com/@test2/live"]
        self.rtmp_url = "rtmp://localhost/live"
        self.stream_key = "test_key"
        self.restreamer = TikTokRestreamer(self.tiktok_urls, self.rtmp_url, self.stream_key, scan_interval=1, overlay_text="Test Link")

    @patch('subprocess.run')
    def test_get_stream_url_success(self, mock_run):
        # Mock successful yt-dlp output
        mock_run.return_value = MagicMock(stdout="https://manifest.tiktok.com/stream.m3u8\n", check=True)
        
        url = self.restreamer.get_stream_url(self.tiktok_urls[0])
        self.assertEqual(url, "https://manifest.tiktok.com/stream.m3u8")
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_get_stream_url_failure(self, mock_run):
        # Mock failed yt-dlp output
        mock_run.side_effect = Exception("Failed")
        
        url = self.restreamer.get_stream_url(self.tiktok_urls[0])
        self.assertIsNone(url)

    @patch('tiktok_restreamer.TikTokRestreamer.get_stream_url')
    @patch('subprocess.Popen')
    def test_start_restream_process(self, mock_popen, mock_get_url):
        # Mock successful URL fetch
        mock_get_url.return_value = "https://mock-stream.url"
        
        # Mock Popen process
        mock_process = MagicMock()
        # Use a list that we can append to if needed, or just a simple iterator
        mock_process.stdout = iter(["frame= 100 fps=30.0 q=-1.0 size= 1024kB time=00:00:05.00 bitrate=1638.4kbits/s speed= 1x"])
        mock_popen.return_value = mock_process
        
        # Prevent the monitor thread from finishing too fast in the test
        # by mocking wait to block until we say so
        mock_process.wait.side_effect = lambda: None 
        
        log_messages = []
        def log_callback(msg):
            log_messages.append(msg)

        self.restreamer.start(log_callback)
        
        # Verify that Popen was called (this confirms the logic reached the execution phase)
        mock_popen.assert_called_once()
        
        # Verify startup logs
        self.assertTrue(any("Checking" in msg for msg in log_messages))
        self.assertTrue(any("Starting restream" in msg for msg in log_messages))

    def test_stop_restream(self):
        # Mock a running process
        self.restreamer.process = MagicMock()
        self.restreamer.is_running = True
        
        self.restreamer.stop()
        
        self.assertFalse(self.restreamer.is_running)
        self.restreamer.process.terminate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
