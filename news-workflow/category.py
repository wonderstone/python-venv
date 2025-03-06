from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

class Category(BaseModel):
    """Category that news should be sorted into."""
    # ! 如果Field提供默认值，Qwen和Deepseek都会返回默认值。
    # todo：未来验证这个部分的内容吧
    Category: Literal["收市综评", "公司新闻", "其他"] = Field(..., description="Category that news should be sorted into.")

    @field_validator("Category",mode="before")
    def validate_category(cls, v):
        valid_categories = ["收市综评", "公司新闻", "其他"]
        # 如果输入的值不在有效范围内，则返回 "其他"
        if v not in valid_categories:
            return "其他"
        return v

if __name__ == "__main__":
    # test valid category
    category = Category(Category="公司新闻")
    print(category)
    # test invalid category
    category = Category(Category="公司")
    print(category)

    # test None category
    category = Category(Category=None)  
    print(category)