import qrcode
import json
from io import BytesIO
import base64
from typing import Dict, Any


def generate_qr_code(ticket_id: int, ticket_number: str, concert_id: int) -> tuple[str, str]:
    """
    Generate QR code for a ticket.
    
    Returns:
        tuple: (qr_code_base64, qr_data_string)
    """
    # Create QR data payload
    qr_data = {
        "ticket_id": ticket_id,
        "ticket_number": ticket_number,
        "concert_id": concert_id,
    }
    
    qr_data_string = json.dumps(qr_data)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data_string)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return qr_base64, qr_data_string


def decode_qr_data(qr_data_string: str) -> Dict[str, Any]:
    """Decode QR data string back to dictionary."""
    return json.loads(qr_data_string)
