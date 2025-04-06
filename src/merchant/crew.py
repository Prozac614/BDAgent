from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from typing import List, Dict
import os

from .tools.google_trend_tool import GoogleTrendTool
from .tools.website_traffic_tool import WebsiteTrafficTool

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

    @agent
    def brand_researcher_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["brand_researcher_analyst"],
            verbose=True,
            tools=[SerperDevTool(), GoogleTrendTool(), WebsiteTrafficTool()],
            llm="deepseek/deepseek-chat",
        )
    
    @agent
    def customer_solutions_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["customer_solutions_specialist"],
            verbose=True,
            tools=[SerperDevTool(), GoogleTrendTool(), WebsiteTrafficTool()],
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
            context=[self.research_analysis_task()],
            config=self.tasks_config["client_contact_information_task"],
        )


    @task
    def brand_researcher_analyst_task(self) -> Task:
        return Task(
            context=[self.research_analysis_task()],
            config=self.tasks_config["brand_researcher_analyst_task"],
        )

    @task
    def customer_solutions_specialist_task(self) -> Task:
        return Task(
            context=[self.brand_researcher_analyst_task()],
            config=self.tasks_config["customer_solutions_specialist_task"],
        )
    
    @task
    def business_development_outreach_specialist_task(self) -> Task:
        return Task(
            context=[self.customer_solutions_specialist_task(), self.brand_researcher_analyst_task(),self.client_contact_information_task()],
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
            manager_llm="deepseek/deepseek-chat",
            process=Process.hierarchical,
            planning=True,
            planning_llm="deepseek/deepseek-chat",
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

class MerchantCrew:
    def __init__(self):
        # 确保设置了 Deepseek API 密钥
        if not os.getenv("DEEPSEEK_API_KEY"):
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        
        # 初始化代理
        self.researcher = Agent(
            role='市场研究员',
            goal='深入研究目标行业和区域的企业信息',
            backstory='我是一名专业的市场研究员，擅长收集和分析企业信息。',
            verbose=True,
            allow_delegation=False,
            llm="deepseek/deepseek-chat",
            tools=[SerperDevTool()]
        )
        
        self.writer = Agent(
            role='商务沟通专家',
            goal='创建专业且个性化的商务沟通内容',
            backstory='我是一名资深的商务沟通专家，擅长撰写专业的商务邮件和沟通内容。',
            verbose=True,
            allow_delegation=False,
            llm="deepseek/deepseek-chat"
        )

    async def find_prospects(self, industry: str, region: str, target_count: int) -> List[Dict]:
        """
        寻找潜在客户
        """
        research_task = Task(
            description=f"""
            在{region}地区寻找{industry}行业的潜在客户。
            需要找到{target_count}个潜在客户。
            对于每个客户，需要提供：
            1. 公司名称
            2. 联系人姓名
            3. 职位
            4. 电子邮件
            5. 公司简介
            
            以JSON格式返回结果。
            """,
            agent=self.researcher
        )

        crew = Crew(
            agents=[self.researcher],
            tasks=[research_task],
            process=Process.sequential,
            manager_llm="deepseek/deepseek-chat",
            planning=True,
            planning_llm="deepseek/deepseek-chat",
            verbose=True
        )

        result = crew.kickoff()
        
        # 这里应该添加结果解析逻辑
        # 示例返回
        return [
            {
                "name": "张三",
                "email": "zhangsan@example.com",
                "company": "示例科技有限公司",
                "position": "技术总监"
            }
            # 实际实现中应该解析 result 并返回真实数据
        ]

    async def generate_engagement(
        self,
        customer_name: str,
        company: str,
        history: List[Dict]
    ) -> Dict:
        """
        生成客户互动内容
        """
        context = "\n".join([
            f"时间：{h['created_at']}\n类型：{h['type']}\n内容：{h['content']}\n"
            for h in history
        ])

        writing_task = Task(
            description=f"""
            为客户{customer_name}（{company}）生成一封跟进邮件。
            
            历史互动记录：
            {context}
            
            要求：
            1. 内容专业且个性化
            2. 参考历史互动记录
            3. 突出我们的价值主张
            4. 明确下一步行动建议
            
            返回JSON格式，包含：
            1. content: 邮件内容
            2. subject: 邮件主题
            3. next_action: 建议的下一步行动
            """,
            agent=self.writer
        )

        crew = Crew(
            agents=[self.writer],
            tasks=[writing_task],
            process=Process.sequential,
            manager_llm="deepseek/deepseek-chat",
            planning=True,
            planning_llm="deepseek/deepseek-chat",
            verbose=True
        )

        result = crew.kickoff()
        
        # 示例返回
        return {
            "content": f"""
            尊敬的{customer_name}：
            
            感谢您一直以来对我们的支持。基于我们之前的沟通，我想跟进一下相关事项...
            
            期待您的回复。
            
            顺祝商祺
            """.strip(),
            "subject": "业务合作跟进",
            "next_action": "等待客户回复后安排线下会议"
        }

    async def generate_initial_contact(
        self,
        customer_name: str,
        company: str
    ) -> Dict:
        """
        生成初始联系内容
        """
        writing_task = Task(
            description=f"""
            为新客户{customer_name}（{company}）生成一封初次联系邮件。
            
            要求：
            1. 简要介绍我们的公司
            2. 说明为什么联系他们
            3. 提供明确的价值主张
            4. 请求进一步沟通的机会
            
            返回JSON格式，包含：
            1. content: 邮件内容
            2. subject: 邮件主题
            """,
            agent=self.writer
        )

        crew = Crew(
            agents=[self.writer],
            tasks=[writing_task],
            process=Process.sequential,
            manager_llm="deepseek/deepseek-chat",
            planning=True,
            planning_llm="deepseek/deepseek-chat",
            verbose=True
        )

        result = crew.kickoff()
        
        # 示例返回
        return {
            "content": f"""
            尊敬的{customer_name}：
            
            我是XXX公司的商务代表。通过了解到贵公司在{company}行业的领先地位，
            我们认为双方有很好的合作机会...
            
            期待有机会进一步沟通。
            
            顺祝商祺
            """.strip(),
            "subject": "商务合作洽谈"
        }
