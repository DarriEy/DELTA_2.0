from google.genai import types

def get_tools_config():
    """Returns the tool configuration for Gemini."""
    
    run_model_tool = types.FunctionDeclaration(
        name="run_model",
        description="Run a hydrological model simulation (e.g., SUMMA, FUSE) for a specific domain.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "model": types.Schema(
                    type=types.Type.STRING,
                    description="The hydrological model to use (SUMMA, FUSE, MESH, etc.)"
                ),
                "domain": types.Schema(
                    type=types.Type.STRING,
                    description="The watershed domain to simulate (e.g., 'Bow_at_Banff_lumped')"
                )
            },
            required=["model"]
        )
    )

    return types.Tool(function_declarations=[run_model_tool])
