from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re


# 输入 schema
class WebsiteTrafficToolInput(BaseModel):
    argument: str = Field(..., description="Target website domain, like 'google.com'")


# 输出 schema
class WebsiteTrafficToolOutput(BaseModel):
    domain: str
    raw_traffic: str
    estimated_visits: float
    conclusion: str


# 工具定义
class WebsiteTrafficTool(BaseTool):
    name: str = "WebsiteTrafficTool"
    description: str = (
        "Get the website traffic data for a given domain using SimilarWeb (via Selenium)."
    )
    args_schema: Type[BaseModel] = WebsiteTrafficToolInput
    output_schema: Type[BaseModel] = WebsiteTrafficToolOutput

    def _parse_traffic_to_number(self, traffic_str: str) -> float:
        """Convert traffic string like '1.2M', '350K', '2B' into a float number."""
        match = re.match(r"([\d.,]+)([KMB]?)", traffic_str.strip().upper())
        if not match:
            return -1
        number, unit = match.groups()
        try:
            number = float(number.replace(",", ""))
        except:
            return -1
        multiplier = {"": 1, "K": 1e3, "M": 1e6, "B": 1e9}.get(unit, 1)
        return number * multiplier

    def _run(self, argument: str) -> WebsiteTrafficToolOutput:
        # 设置 Selenium
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(f"https://www.similarweb.com/website/{argument}/")
            time.sleep(5)  # 等待 JS 渲染
            traffic_str = driver.find_element(
                By.CSS_SELECTOR, '[data-testid="total-visits-value"]'
            ).text
        except Exception as e:
            traffic_str = f"Not found or blocked ({str(e)})"
            estimated = -1
            conclusion = "无法判断（抓取失败）"
        else:
            estimated = self._parse_traffic_to_number(traffic_str)

            # 结论逻辑
            if estimated >= 1e8:
                conclusion = "超级高流量（≥ 100M/月）"
            elif estimated >= 1e7:
                conclusion = "高流量(10M ~ 100M/月）"
            elif estimated >= 1e6:
                conclusion = "中等流量(1M ~ 10M/月）"
            elif estimated >= 1e5:
                conclusion = "流量偏低(100K ~ 1M/月）"
            elif estimated >= 0:
                conclusion = "极低流量(< 100K/月）"
            else:
                conclusion = "无法判断（格式异常）"
        finally:
            driver.quit()

        return WebsiteTrafficToolOutput(
            domain=argument,
            raw_traffic=traffic_str,
            estimated_visits=estimated,
            conclusion=conclusion,
        )


# 用于测试
if __name__ == "__main__":
    tool = WebsiteTrafficTool()
    test_input = WebsiteTrafficToolInput(argument="google.com")
    result = tool._run(argument=test_input.argument)
    print(result.model_dump_json(indent=2))
