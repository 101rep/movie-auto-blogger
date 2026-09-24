from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

Goal=Literal["INFORMATION","ENGAGEMENT","TRUST","AFFILIATE"]
Angle=Literal["EXPERIENCE","PROBLEM_SOLUTION","COMPARE_SELECT","PRICE_SAVING"]
Hook=Literal["NUMBER","FAILURE","REVERSAL","CLAIM","CONFESSION","OBSERVATION","SURPRISE","COST","COMPARISON"]
class Strict(BaseModel):
    model_config=ConfigDict(extra="forbid")
class LoginIn(Strict):
    username:str=Field(min_length=1,max_length=80)
    password:str=Field(min_length=1,max_length=256)
class AccountIn(Strict):
    name:str=Field(min_length=1,max_length=100)
    username:str=Field(pattern=r"^[a-zA-Z0-9_.-]{1,100}$")
    category:str=Field(min_length=1,max_length=80)
    timezone:str="Asia/Seoul"
    daily_post_limit:int=Field(default=3,ge=1,le=50)
    daily_affiliate_limit:int=Field(default=1,ge=0,le=20)
    minimum_interval:int=Field(default=60,ge=1,le=1440)
    affiliate_ratio:float=Field(default=0.2,ge=0,lt=1)
    reply_count:int=Field(default=1,ge=1,le=3)
    content_ratios:dict[str,int]=Field(default_factory=lambda:{"INFORMATION":50,"ENGAGEMENT":20,"TRUST":10,"AFFILIATE":20})
    status:Literal["ONLINE","PAUSED","ERROR","AUTH_REQUIRED"]="ONLINE"
    access_token_reference:str|None=Field(default=None,pattern=r"^THREADS_TOKEN_[A-Z0-9_]+$")
    @field_validator("timezone")
    @classmethod
    def tz(cls,v):
        try: ZoneInfo(v)
        except ZoneInfoNotFoundError: raise ValueError("Unknown timezone")
        return v
    @model_validator(mode="after")
    def ratios(self):
        if set(self.content_ratios)!={"INFORMATION","ENGAGEMENT","TRUST","AFFILIATE"} or sum(self.content_ratios.values())!=100 or min(self.content_ratios.values())<0 or self.content_ratios["AFFILIATE"]>=100:
            raise ValueError("Ratios must sum to 100 with affiliate below 100")
        if self.daily_affiliate_limit>self.daily_post_limit: raise ValueError("Affiliate limit exceeds daily limit")
        if abs(self.content_ratios["AFFILIATE"]/100-self.affiliate_ratio)>0.001: raise ValueError("Affiliate ratio must match content ratios")
        return self
class PersonaIn(Strict):
    target_description:str=Field(default="",max_length=500)
    primary_desire:str=Field(default="시간 절약",max_length=200)
    secondary_desire:str=Field(default="돈 절약",max_length=200)
    pain_points:list[str]=Field(default_factory=list,max_length=20)
    tone:str=Field(default="친근한",max_length=80)
    speech_style:Literal["존댓말","반말"]="존댓말"
    emoji_level:int=Field(default=0,ge=0,le=1)
    hook_preferences:list[Hook]=Field(default_factory=list,max_length=9)
    prohibited_styles:list[str]=Field(default_factory=list,max_length=20)
    content_objectives:list[Goal]=Field(default_factory=list,max_length=4)
class SourceIn(Strict):
    name:str=Field(min_length=1,max_length=120)
    type:Literal["MANUAL","RSS","WEB","API","REDDIT","NEWS","TREND","CUSTOM"]="MANUAL"
    url:str|None=Field(default=None,max_length=2000)
class ContentIn(Strict):
    source_id:int
    source_title:str=Field(min_length=2,max_length=200)
    source_text:str=Field(min_length=10,max_length=20000)
    source_url:str|None=Field(default=None,max_length=2000)
    category:str=Field(min_length=1,max_length=80)
class GenerateIn(Strict):
    account_id:int
    goal:Goal="INFORMATION"
    angle:Angle="PROBLEM_SOLUTION"
    hook_type:Hook="OBSERVATION"
    product_id:int|None=None
class PostEdit(Strict):
    body:str=Field(min_length=1,max_length=500)
    replies:list[str]=Field(default_factory=list,max_length=3)
    @field_validator("replies")
    @classmethod
    def length(cls,v):
        if any(not x.strip() or len(x)>500 for x in v): raise ValueError("Reply must be 1–500 characters")
        return v
class ScheduleIn(Strict):
    scheduled_at:datetime|None=None
    window_start:datetime|None=None
    window_end:datetime|None=None
    jitter_seconds:int=Field(default=0,ge=0,le=3600)
    @field_validator("scheduled_at","window_start","window_end")
    @classmethod
    def aware(cls,v):
        if v is not None and v.tzinfo is None: raise ValueError("Timezone offset required")
        return v
    @model_validator(mode="after")
    def window(self):
        if bool(self.window_start)!=bool(self.window_end): raise ValueError("Both window boundaries required")
        if self.window_start and (self.scheduled_at or self.window_end<=self.window_start): raise ValueError("Invalid window")
        return self
class SettingIn(Strict):
    global_daily_limit:int=Field(default=15,ge=1,le=200)
    cooldown_days:int=Field(default=14,ge=1,le=365)
    similarity_threshold:float=Field(default=0.86,ge=0.5,le=0.99)
    disclosure:str=Field(default="이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.",min_length=15,max_length=200)
class CommandIn(Strict):
    chat_id:str=Field(max_length=100)
    text:str=Field(min_length=1,max_length=300)
class ProductSelectIn(Strict):
    keyword:str=Field(min_length=1,max_length=100)
    account_id:int|None=None
    limit:int=Field(default=10,ge=1,le=50)
class DeeplinkIn(Strict):
    urls:list[str]=Field(min_length=1,max_length=20)
    sub_id:str|None=Field(default=None,max_length=50)

class InstagramAccountIn(Strict):
    instagram_id:str|None=None
    business_account_id:str|None=None
    access_token:str|None=None
    status:Literal['ONLINE','PAUSED','ERROR']='ONLINE'
    threads_ratio:float=Field(default=0.5,ge=0.0,le=1.0)
    instagram_ratio:float=Field(default=0.3,ge=0.0,le=1.0)
    blog_ratio:float=Field(default=0.2,ge=0.0,le=1.0)

class CardnewsGenerateIn(Strict):
    title:str=Field(min_length=2,max_length=200)
    template:str=Field(default='minimal')
    content_type:str=Field(default='CAROUSEL')

class InstagramPostIn(Strict):
    account_id:int
    content_id:int|None=None
    media_type:str='CAROUSEL'
    title:str=Field(min_length=1,max_length=200)
    caption:str=Field(min_length=1,max_length=2200)
    carousel_data:dict=Field(default_factory=dict)
    media_urls:list[str]=Field(default_factory=list)

class AIGenerateIn(Strict):
    task_type:Literal['research','strategy','writing','cardnews','product','review','analytics']='writing'
    prompt:str=Field(min_length=1,max_length=10000)
    account_id:int|None=None
    force_provider:str|None=None
