"""
벨류업 기능 테스트 스크립트
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.trend_collector import trend_collector_service
from services.context_collector import context_collector_service
from services.story_generator import story_generator_service

print("=" * 60)
print("Value-up Feature Test")
print("=" * 60)

# 1. Trend Collection Test
print("\n[1] Real-time Trend Collection Test")
print("-" * 60)
trends = trend_collector_service.get_trends(limit=10)
print(f"Collected trends ({len(trends)}):")
for i, trend in enumerate(trends, 1):
    print(f"  {i}. {trend}")

# 2. Menu-specific Trends
print("\n[2] Menu-specific Trends Test")
print("-" * 60)
menu_trends = trend_collector_service.get_trending_keywords_for_menu(['커피', '디저트'])
print(f"Coffee/Dessert related trends:")
for i, trend in enumerate(menu_trends, 1):
    print(f"  {i}. {trend}")

# 3. Context Collection (with trends)
print("\n[3] Context Collection Test (with trends)")
print("-" * 60)
context = context_collector_service.get_full_context(
    location="Seoul",
    menu_categories=['커피', '디저트']
)
print(f"Weather: {context['weather']['description']}, {context['weather']['temperature']}C")
print(f"Season: {context['season']}")
print(f"Time: {context['time_info']['period_kr']}")
print(f"Trends: {context['trends']}")

# 4. Single Story Generation (Prompt Improvement Check)
print("\n[4] Single Story Generation Test (Improved Prompt)")
print("-" * 60)
story = story_generator_service.generate_story(
    context=context,
    store_name="Seoul Cafe",
    store_type="cafe",
    menu_categories=["coffee", "dessert"]
)
print(f"Generated story:")
print(f"   \"{story}\"")

# 5. A/B Test (Multiple Versions)
print("\n[5] A/B Test - Multiple Versions")
print("-" * 60)
stories = story_generator_service.generate_multiple_stories(
    context=context,
    store_name="Seoul Cafe",
    store_type="cafe",
    menu_categories=["coffee", "dessert"],
    count=3
)
print(f"Generated 3 versions:")
for i, story_variant in enumerate(stories, 1):
    print(f"\n  Version {i}:")
    print(f"  \"{story_variant}\"")

# 6. Brand Tone Differentiation Test
print("\n[6] Brand Tone Differentiation Test")
print("-" * 60)
store_types = ["cafe", "restaurant", "dessert", "pub"]
for store_type in store_types:
    story = story_generator_service.generate_story(
        context=context,
        store_name=f"Test {store_type}",
        store_type=store_type,
        menu_categories=["menu1", "menu2"]
    )
    print(f"\n  [{store_type}] \"{story}\"")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
