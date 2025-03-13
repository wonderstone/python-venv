from typing import Any, List, Literal, Type
from pydantic import BaseModel, Field, field_validator

class CategoryFactory:
    def __init__(self, valid_categories: List[str]):
        self.valid_categories = valid_categories

    def create_category_model(self) -> Type[BaseModel]:
        valid_categories_literal = Literal[tuple(self.valid_categories)]

        class Category(BaseModel):
            """Category that news should be sorted into."""
            # ! 这里提示，但仍然可以运行。type annotations intended to be static type hints rather than variable or function expressions
            # ! 如果为了完成抽象一层的任务，大概率要考虑更换方法。重构的时候，要考虑这个问题。
            Category: valid_categories_literal = Field(..., description="Category that news should be sorted into.")

            @field_validator("Category", mode="before")
            def validate_category(cls, v):
                if v not in self.valid_categories:
                    return "其他"
                return v

        return Category

if __name__ == "__main__":
    # 从外部输入定义有效的类别
    valid_categories = ["收市综评", "公司新闻", "其他", "国际新闻", "体育新闻"]

    # 创建工厂实例
    factory = CategoryFactory(valid_categories)

    # 创建类别模型
    Category = factory.create_category_model()

    # 测试有效类别
    category = Category(Category="公司新闻")
    print(category)

    # 测试无效类别
    category = Category(Category="无效类别")
    print(category)

    # 测试 None 类别
    category = Category(Category=None)
    print(category)