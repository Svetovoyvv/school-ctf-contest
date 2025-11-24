import os
import zipfile
import shutil

def create_challenge():
    flag = os.environ.get('FLAG', 'ctf{test_flag}')
    
    # Determine output directory
    # If running in docker as mapped in compose
    if os.path.isdir('/app/output'):
        output_dir = '/app/output'
    else:
        # Local fallback
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Using output directory: {output_dir}")

    # Create flag file
    with open('flag.txt', 'w') as f:
        f.write(flag)
    
    # Create zip file with compression
    zip_filename = 'confidential.zip'
    with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        zipf.write('flag.txt')
    
    # Modify signature
    # Standard ZIP header: 50 4B 03 04 (PK\x03\x04)
    # We change it to:     57 48 4F ?? (WHO??)
    # The prompt says: "first 3 bytes make WHO"
    
    with open(zip_filename, 'r+b') as f:
        f.seek(0)
        f.write(b'WHO')
        
    # Move to output
    dest_path = os.path.join(output_dir, zip_filename)
    
    # Remove destination if exists
    if os.path.exists(dest_path):
        os.remove(dest_path)
        
    # Move file
    shutil.move(zip_filename, dest_path)
    
    # Clean up flag.txt
    if os.path.exists('flag.txt'):
        os.remove('flag.txt')

    print(f"Challenge generated at {dest_path}")

if __name__ == "__main__":
    create_challenge()
