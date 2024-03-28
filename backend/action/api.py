import requests
from openai import OpenAI
import re

class Action(object):

    def __init__(self):
        self.client = OpenAI()
    
    def calculate_bmi(self, height, weight, age):
    
        bmi = weight / ((height / 100) ** 2)
        
        consumption = 1.2 * (655 + (9.6 * weight) + (1.8 * height) - (4.7 * age))
        return bmi, consumption

    def parse_height(self,height_str):
        
        match = re.match(r"(\d+(\.\d+)?)[\s]?(cm|in|inches)$", height_str, re.IGNORECASE)
        if match:
            value, _, unit = match.groups()
            if 'cm' in unit.lower():
                return float(value)
            elif 'in' in unit.lower():  # Covers 'in' and 'inches'
                return float(value) * 2.54  # 英寸到厘米的转换
        return None  # 未匹配或格式错误

    def parse_weight(self,weight_str):
        
        match = re.match(r"(\d+(\.\d+)?)[\s]?(kg|lb|pounds)$", weight_str, re.IGNORECASE)
        if match:
            value, _, unit = match.groups()
            if 'kg' in unit.lower():
                return float(value)
            elif 'lb' in unit.lower() or 'pounds' in unit.lower():
                return float(value) * 0.453592  # 磅到千克的转换
        return None  # 未匹配或格式错误

    def calculate_bmi_and_diet_plan(self, slots):
        height_str = slots["height"]
        weight_str = slots["weight"]
        age = int(slots["age"])

        fitness_program = slots["fitness_program"]
        avoid_eating = slots["avoid_eating"]

        height = self.parse_height(height_str)
        weight = self.parse_weight(weight_str)
        print(height)
        print(weight)

        bmi, consumption = self.calculate_bmi(height, weight, age)
        bmi = weight / ((height / 100) ** 2)
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":f"Given that a person has a BMI of {bmi:.2f} and a daily calorie consumption of roughly {consumption:.2f} calories, this person is avoiding eating {avoid_eating}, and fitness program is {fitness_program}, recommend a diet plan for that person. (Output only the diet plan and don't say anything else.)"}
                ],
            max_tokens=150,
        )
        diet_plan_content = response.choices[0].message.content
        return f"Hello, your BMI is {bmi:.2f}, your daily calorie consumption is roughly {consumption:.2f} calories, and the recommended diet plan is:\n{diet_plan_content}"


    def calculate_calorie_intake(self,slots):
        foods = slots["food"]
        quantities = slots["weight_or_number"]
        # 示例：调用GPT模型计算食物的卡路里
        if len(foods) != len(quantities):
            return "Error: Foods and quantities lists must have the same length."
        prompt_parts = []
        prompt_parts.append("Calculate the total calories for:\n")
        for food, quantity in zip(foods, quantities):
            prompt_parts.append(f"{quantity} of {food}.")
        prompt = " ".join(prompt_parts)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":prompt}
                ],
            max_tokens=150,
        )
        return f"here is the calories calculation steps:\n {response.choices[0].message.content}."


    def recommend_recipes_based_on_ingredients(self,slots):
        ingredients = slots["ingredient"]
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":f"Recommend recipes based on these ingredients: {', '.join(ingredients)}."}
                ],
            max_tokens=150,
        )
        return  response.choices[0].message.content


    def provide_detailed_steps_for_recipe(self,slots):
        recipe_name = slots["recipe_name"]
        url = 'https://recipe-by-api-ninjas.p.rapidapi.com/v1/recipe'
        querystring = {"query":recipe_name}
        recipe_details = requests.get(url, headers={"X-RapidAPI-Key": "1c01dcf72dmsh8296e51e1f304d4p1928b3jsna74b0dcebb0f", "X-RapidAPI-Host": "recipe-by-api-ninjas.p.rapidapi.com"},params=querystring)
        response_dict = recipe_details.json()
        if response_dict == []:
            return "We apologize for not finding the recipe you were searching for."
        else:
            response = response_dict[1]
            return f"The steps you need to complete if you want to make a {response['title']} are: {response['instructions']}"


    def handle_out_of_scope():
        return "I'm sorry we can't support your request at this time, I can help you in these areas below: 1: 'Designing a diet plan', 2: 'Calculate calorie intake', 3: 'Recommend recipes based on ingredients', 4: 'Provide detailed steps for recipes'."

    def api_handler(self, meaasge_dict):
        intent = meaasge_dict["intent"]
        slots = meaasge_dict["slots"]
        if intent == 1:
            return self.calculate_bmi_and_diet_plan(slots)
        elif intent == 2:
            return self.calculate_calorie_intake(slots)
        elif intent == 3:
            return self.recommend_recipes_based_on_ingredients(slots)
        elif intent == 4:
            return self.provide_detailed_steps_for_recipe(slots)
        elif intent == 5:
            return self.handle_out_of_scope()
        else:
            return "Invalid intent."


