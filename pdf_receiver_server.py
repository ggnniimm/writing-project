#!/usr/bin/env python3
"""
HTTP Server to receive PDF base64 data from browser
This bypasses all download/file dialog restrictions
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import base64
import json

class PDFReceiverHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Receive PDF base64 data via POST"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Parse JSON data
            data = json.loads(post_data.decode('utf-8'))
            base64_data = data.get('base64')
            
            if not base64_data:
                self.send_error(400, "No base64 data provided")
                return
            
            # Decode and save PDF
            pdf_binary = base64.b64decode(base64_data)
            output_path = "raw_pdfs/sac_o_105_2566.pdf"
            
            with open(output_path, 'wb') as f:
                f.write(pdf_binary)
            
            file_size_mb = len(pdf_binary) / (1024 * 1024)
            
            # Verify PDF
            is_valid = pdf_binary[:4] == b'%PDF'
            
            response = {
                'success': True,
                'file': output_path,
                'size_bytes': len(pdf_binary),
                'size_mb': round(file_size_mb, 2),
                'is_valid_pdf': is_valid
            }
            
            print(f"\n✅ Received PDF data!")
            print(f"📏 Size: {len(pdf_binary):,} bytes ({file_size_mb:.2f} MB)")
            print(f"💾 Saved to: {output_path}")
            print(f"✓ Valid PDF: {is_valid}\n")
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
            # Shutdown server after successful save
            print("🛑 Shutting down server...\n")
            import threading
            threading.Thread(target=self.server.shutdown).start()
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"❌ {error_msg}")
            self.send_error(500, error_msg)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging except errors"""
        if '500' in str(args) or '400' in str(args):
            super().log_message(format, *args)

def run_server(port=8765):
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, PDFReceiverHandler)
    print(f"🚀 PDF Receiver Server started on http://localhost:{port}")
    print(f"📡 Waiting for browser to send PDF data...")
    print(f"   (Server will auto-shutdown after receiving data)\n")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
