
from django.shortcuts import render
from django.contrib import messages
from PIL import Image, UnidentifiedImageError
from transformers import pipeline
from functools import lru_cache


MODEL_NAME = "neghani/plantvillage-mobilenetv2"


@lru_cache(maxsize=1)
def load_plant_model():
    return pipeline(
        "image-classification",
        model=MODEL_NAME,
        device=-1
    )


def plant_checker(request):

    if request.method == "POST":

        plant_image = request.FILES.get("plant_image")

        if not plant_image:
            messages.error(request, "Please upload a plant image.")
            return render(request, "plant_health/checker.html")

        if plant_image.size > 10 * 1024 * 1024:
            messages.error(request, "Image size must be below 10 MB.")
            return render(request, "plant_health/checker.html")

        try:
            # Read the uploaded image
            with Image.open(plant_image) as img:
                image = img.convert("RGB")

            # Load the AI model and predict
            model = load_plant_model()
            predictions = model(image, top_k=1)

            prediction = predictions[0]

            label = prediction["label"]
            confidence = prediction["score"]

            # Separate crop name and disease name
            parts = label.split("___", 1)

            crop_name = parts[0].replace("_", " ").replace(",", "")
            condition = (
                parts[1].replace("_", " ").strip()
                if len(parts) > 1
                else "Unknown"
            )

            if confidence < 0.50:
                status = "Uncertain"
                condition = "Unable to identify reliably"
            elif "healthy" in condition.lower():
                status = "Healthy"
            else:
                status = "Possible Disease Detected"

            context = {
                "image_uploaded": True,
                "crop_name": crop_name,
                "condition": condition,
                "confidence": round(confidence * 100, 2),
                "status": status,
            }

            return render(
                request,
                "plant_health/checker.html",
                context
            )

        except (UnidentifiedImageError, OSError):
            messages.error(
                request,
                "Invalid image. Please upload a valid JPG or PNG image."
            )

        except Exception as e:
            print("Plant detection error:", str(e))
            messages.error(
                request,
                "Unable to analyse the image. Check your AI library installation and internet connection."
            )

    return render(request, "plant_health/checker.html")
