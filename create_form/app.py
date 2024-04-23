import requests

# Define the form data
form_data = {
    "title": "My Form",
    "description": "This is a sample form created using the Google Forms API.",
    "imageUrl": "https://example.com/image.jpg",
    "fields": [
        {
            "type": "text",
            "label": "Name",
            "isRequired": True
        },
        {
            "type": "image",
            "label": "Image",
            "isRequired": False
        },
        {
            "type": "scale",
            "label": "Rating",
            "isRequired": True,
            "scaleLabels": ["Poor", "Fair", "Good", "Excellent"]
        }
    ]
}

# Send a POST request to create the form
response = requests.post("https://www.googleapis.com/forms/v1/forms", json=form_data)

# Check the response status code
if response.status_code == 200:
    form_id = response.json()["formId"]
    print(f"Form created successfully! Form ID: {form_id}")
else:
    print("Failed to create the form.")