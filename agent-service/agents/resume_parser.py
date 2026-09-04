from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from services.llm_service import LLMService
from pydantic import BaseModel, Field

class Education(BaseModel):
    school : str = Field(description="学校名称")
    major : str = Field(description="专业")
    degree : str = Field(description="学历")
    graduation_year : str = Field(description="毕业年份")

class Skills(BaseModel):
    languages: List[str] = Field(description="编程语言")
    frameworks: List[str] = Field(description="框架")
    databases: List[str] = Field(description="数据库")
    tools: List[str] = Field(description="工具")

class Project(BaseModel):
    name: str = Field(description="项目名称")
    description: str = Field(description="项目描述")
    tech_stack: List[str] = Field(description="技术栈")
    achievements: List[str] = Field(description="成果")

class Internship(BaseModel):
    company: str = Field(description="公司")
    position: str = Field(description="职位")
    duration: str = Field(description="时间")
    description: str = Field(description="描述")

class Experience(BaseModel):
    projects: List[Project] = Field(description="项目经验")
    internships: List[Internship] = Field(description="实习经历", default=[])

class ResumeData(BaseModel):
    name : str = Field(description="姓名")
    email : str = Field(description="邮箱")
    phone : str = Field(description="电话号码")
    education : Education = Field(description="教育背景")
    skills : Skills = Field(description="技能")
    experience : Experience = Field(description="经历")

class ResumeParseAgent:
    def __init__(self):
        self.llm_service = LLMService()
        self.llm = self.llm_service.get_llm()
        self.parser = PydanticOutputParser(pydantic_object=ResumeData)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system","你是一个专业的简历解析助手，请从简历中提取关键信息。"),
            ("user","简历内容：\n{resume_text}\n\n{format_instructions}")
        ])
        self.chain = self.prompt | self.llm | self.parser

    def parse(self, resume_text: str) -> dict:
        """解析简历"""
        try:
            result = self.chain.invoke({
                "resume_text": resume_text,
                "format_instructions": self.parser.get_format_instructions()
            })
            return {
                "success": True,
                "data": result.dict()
            }
        except Exception as e:
            print(f"简历解析失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }