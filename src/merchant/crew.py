from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class Merchant:
    """Merchant crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def global_business_research_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["global_business_research_analyst"],
            verbose=True,
            tools=[SerperDevTool()],
            llm="deepseek/deepseek-chat",
        )

    @agent
    def client_contact_information_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["client_contact_information_specialist"],
            verbose=True,
            tools=[SerperDevTool()],
            llm="deepseek/deepseek-chat",
        )

    @agent
    def business_development_outreach_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["business_development_outreach_specialist"],
            verbose=True,
            tools=[SerperDevTool()],
            llm="deepseek/deepseek-chat",
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_analysis_task"],
        )

    @task
    def client_contact_information_task(self) -> Task:
        return Task(
            config=self.tasks_config["client_contact_information_task"],
        )

    @task
    def business_development_outreach_specialist_task(self) -> Task:
        return Task(
            config=self.tasks_config["business_development_outreach_specialist_task"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Merchant crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
