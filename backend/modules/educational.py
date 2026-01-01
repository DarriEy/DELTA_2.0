# backend/modules/educational.py

class EducationalModule:
    def get_educational_content(self, topic: str) -> str:
        """Provides educational content on the given topic.

        For now, this is a simplified example. In a full implementation,
        this would likely involve querying a knowledge base or generating
        content dynamically using the LLM.
        """
        topic_lower = topic.lower()
        if topic_lower == "hydrological cycle":
            return """
            The hydrological cycle, also known as the water cycle, is the continuous movement of water on, above, and below the surface of the Earth.

            Key processes include:
            * Evaporation: Water changes from liquid to vapor, primarily from oceans and other water bodies.
            * Condensation: Water vapor cools and changes back into liquid, forming clouds.
            * Precipitation: Water falls back to Earth as rain, snow, sleet, or hail.
            * Infiltration: Water soaks into the ground, replenishing groundwater.
            * Runoff: Water flows over the land surface, eventually reaching rivers, lakes, and oceans.
            * Transpiration: Water is released into the atmosphere by plants.

            Understanding the hydrological cycle is fundamental to hydrological modeling.
            """
        elif topic_lower == "watershed":
            return """
            A watershed, also called a drainage basin or catchment, is an area of land where all surface water converges to a single point, typically a river, lake, or ocean.

            Key characteristics of a watershed include:
            * Area: The total land area draining to a common outlet.
            * Slope: The steepness of the terrain, which influences runoff velocity.
            * Land Cover: The type of vegetation and land use, which affects infiltration and evapotranspiration.
            * Soil Type: The characteristics of the soil, which determine infiltration capacity and water storage.

            Watersheds are important units for hydrological analysis and management.
            """
        else:
            return f"Sorry, I don't have information on '{topic}' yet. I can provide information on 'hydrological cycle' or 'watershed'."

def get_educational_module() -> EducationalModule:
    return EducationalModule()
