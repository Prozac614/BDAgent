import os
from dotenv import load_dotenv
from typing import Type
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import Field, BaseModel
from langchain_community.utilities import GoogleTrendsAPIWrapper

# Set up your SERPER_API_KEY key in an .env file, eg:
# SERPER_API_KEY=<your api key>
# load_dotenv()

google_trends = GoogleTrendsAPIWrapper()


class GoogleTrendToolInput(BaseModel):
    argument: str = Field(
        ..., description="The search term to get Google Trends data for."
    )


class GoogleTrendTool(BaseTool):
    name: str = "GoogleTrendTool"
    description: str = "Get the latest Google Trends data for a given query."

    args_schema: Type[BaseModel] = GoogleTrendToolInput

    search: GoogleTrendsAPIWrapper = Field(default_factory=GoogleTrendsAPIWrapper)

    def _run(self, argument: str) -> str:
        """Execute the search query and return results"""
        try:
            return self.google_trends.run(argument)
        except Exception as e:
            return f"Error performing search: {str(e)}"
