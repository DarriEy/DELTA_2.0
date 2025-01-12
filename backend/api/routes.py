from fastapi import APIRouter, HTTPException
from .llm_integration import generate_response, generate_image
from .schemas import UserInput, ImagePrompt
import yaml
import subprocess

router = APIRouter()

@router.post("/api/process")
async def process_input(user_input: UserInput):
    try:
        llm_response = await generate_response(user_input.user_input)
        return {"llmResponse": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/learn")
async def learn_input(user_input: UserInput):
    try:
        llm_response = await generate_response(user_input.user_input, "EDUCATIONAL_GUIDE")
        return {"llmResponse": llm_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate_image")
async def generate_image_route(prompt_data: ImagePrompt):
    try:
        data_uri = await generate_image(prompt_data.prompt)
        if data_uri:
            return {"image_url": data_uri}
        else:
            raise HTTPException(status_code=500, detail="Image generation failed")
    except Exception as e:
        print(f"Error in generate_image_route: {e}")
        # Customize error messages based on the exception type
        if isinstance(e, HTTPException):
            raise e  # Re-raise HTTPException instances to retain their status codes
        elif "specific error condition" in str(e):
            raise HTTPException(status_code=400, detail="Invalid prompt: specific error condition")
        else:
            raise HTTPException(status_code=500, detail="Image generation failed due to an unexpected error")
        

@router.post("/api/run_confluence")
async def run_confluence(input_data: dict):
    try:
        model = input_data.get("model")
        config_path = input_data.get("configPath")

        # Load and update the configuration file
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        config['HYDROLOGICAL_MODEL'] = model

        # Save the updated configuration file
        with open(config_path, 'w') as f:
            yaml.safe_dump(config, f)

        # Run CONFLUENCE using subprocess
        confluence_path = "/Users/darrieythorsson/compHydro/code/CONFLUENCE/CONFLUENCE.py"  # Replace with the actual path to confluence.py
        process = subprocess.run(
            ["python", confluence_path, "--config", config_path],
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=process.stderr)

        return {"message": "CONFLUENCE run started", "output": process.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))