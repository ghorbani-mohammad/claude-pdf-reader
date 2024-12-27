import os
import base64
from typing import Optional
from anthropic import Anthropic


client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    default_headers={"anthropic-beta": "pdfs-2024-09-25"},
)

MODEL_NAME = "claude-3-5-sonnet-20241022"


def get_completion(client, messages):
    return (
        client.messages.create(
            model=MODEL_NAME,
            max_tokens=8192,
            messages=messages,
        )
        .content[0]
        .text
    )


def extract_data_from_file(
    prompt:str, file_name: Optional[str] = None
):
    # Process each split PDF file
    with open(file_name, "rb") as pdf_file:
        binary_data = pdf_file.read()
        base64_encoded_data = base64.standard_b64encode(binary_data)
        base64_string = base64_encoded_data.decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": base64_string,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }
    ]
    
    data = None
    try:
        data = get_completion(client, messages)
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Error extracting data from {file_name}, please try again. Error: {e}")

    print(f"Extracted data: {data}")
    return data

PROMPT = """
Please extract these data from the provided content and return them in the csv format.

1. Commodity (e.g. Sun complex, Soy Complex, Rape Complex, Safflower Complex, Lin Complex, Cotton Complex, Corn Oil Complex, Palm Oil Complex, Olive Oil Complex, Grain Complex) 
2. Spec (like (40 basis, Local Oil-bearing Sunflower) and (Local Crude Sunoil) and (35/36 P Imported Sunmeal, BSea, Nov24, Pel.) and ...)
3. Delivery (like EXW Thrace, CIF Marmara, Ex-Truck Anatolia, and ....)
4. Today (like 21750 +/- 250 TL/mt, 1150 - 1175 $/mt)
"""

extracted_data = extract_data_from_file(PROMPT, "2024_10_25.pdf")
print(extracted_data)

# Save the extracted data to a file
with open("extracted_data.csv", "w") as f:
    f.write(extracted_data)
