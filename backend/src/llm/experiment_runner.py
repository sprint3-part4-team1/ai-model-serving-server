"""
LLM 실험 러너
동일 프롬프트로 여러 모델 실험 및 비교 분석
"""

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .gpt5_provider import GPT5Provider
from .gpt4_provider import GPT4Provider
from .gemini_provider import GeminiProvider
from .base_provider import BaseLLMProvider


class ExperimentRunner:
    """
    LLM 실험 러너
    - 동일 프롬프트로 여러 모델 실험
    - 응답 품질, 속도, 비용 비교
    - 결과 저장 및 분석
    """
    
    def __init__(self):
        self.providers = {
            "gpt-5.1": GPT5Provider(),
            "gpt-4.1": GPT4Provider(),
            "gemini-2.5-flash": GeminiProvider()
        }
        self.experiments = []
    
    def run_experiment(
        self, 
        prompt: str, 
        models: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        여러 모델로 동일 프롬프트 실행
        
        Args:
            prompt (str): 실험할 프롬프트
            models (list): 실험할 모델 리스트 (None이면 전체)
            **kwargs: 모델별 추가 파라미터
        
        Returns:
            dict: {
                "experiment_id": "exp_20251127_001",
                "prompt": "...",
                "timestamp": "2025-11-27T11:00:00",
                "results": {
                    "gpt-5-mini": {...},
                    "gpt-4o": {...},
                    "gemini-2.5-flash": {...}
                }
            }
        """
        # 실험 ID 생성
        exp_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print("=" * 80)
        print(f"🔬 실험 시작: {exp_id}")
        print("=" * 80)
        print(f"프롬프트: {prompt[:100]}...")
        print()
        
        # 실험할 모델 선택
        target_models = models or list(self.providers.keys())
        
        results = {}
        
        for model_name in target_models:
            if model_name not in self.providers:
                print(f"⚠️ {model_name}: 지원하지 않는 모델")
                continue
            
            provider = self.providers[model_name]
            
            print(f"🚀 {model_name} 실행 중...")
            
            # ✅ 초기화!
            json_parsable = False
            parsed_data = None

            try:
                # 응답 생성
                start_time = time.time()
                response = provider.create_response(prompt, **kwargs)
                elapsed_time = time.time() - start_time
                
                # 토큰 수 추정 (간단한 계산)
                input_tokens = len(prompt.split()) * 1.3  # 대략적 추정
                output_tokens = len(response.split()) * 1.3
                
                # 비용 계산
                cost_info = provider.get_cost_per_1k_tokens()
                estimated_cost = (
                    (input_tokens / 1000) * cost_info['input'] +
                    (output_tokens / 1000) * cost_info['output']
                )
                
                try:
                    parsed_data = provider.parse_json_response(response)
                    json_parsable = True
                    print(f"  ✓ JSON 파싱 성공")
                except Exception as parse_error:
                    json_parsable = False
                    print(f"  ✗ JSON 파싱 실패: {str(parse_error)[:50]}")

                results[model_name] = {
                    "success": True,
                    "response": response,
                    "elapsed_time": elapsed_time,
                    "input_tokens": int(input_tokens),
                    "output_tokens": int(output_tokens),
                    "estimated_cost": estimated_cost,
                    "json_parsable": json_parsable,
                    "parsed_data": parsed_data,
                    "response_length": len(response)
                }
                
                print(f"  ✅ 성공 ({elapsed_time:.2f}s, ${estimated_cost:.6f})")
                print(f"  📊 토큰: {int(input_tokens)} in / {int(output_tokens)} out")
                print(f"  📝 응답 길이: {len(response)} chars")
                print()
            
            except Exception as e:
                results[model_name] = {
                    "success": False,
                    "error": str(e),
                    "elapsed_time": 0,
                    "estimated_cost": 0,
                    "json_parsable": False
                }
                print(f"  ❌ 실패: {e}")
                print()
        
        # 실험 결과 저장
        experiment_data = {
            "experiment_id": exp_id,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat(),
            "models_tested": target_models,
            "results": results
        }
        
        self.experiments.append(experiment_data)
        
        print("=" * 80)
        print("✅ 실험 완료")
        print("=" * 80)
        
        return experiment_data
    
    def compare_results(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        실험 결과 비교 분석
        
        Args:
            experiment_data: run_experiment()의 반환값
        
        Returns:
            dict: 비교 분석 결과
        """
        results = experiment_data['results']
        
        # 성공한 모델만 추출
        successful = {
            model: data for model, data in results.items() 
            if data.get('success', False)
        }
        
        if not successful:
            return {"error": "성공한 모델이 없습니다"}
        
        # 순위 계산
        rankings = {
            "speed": sorted(successful.items(), key=lambda x: x[1]['elapsed_time']),
            "cost": sorted(successful.items(), key=lambda x: x[1]['estimated_cost']),
            "response_length": sorted(successful.items(), key=lambda x: x[1]['response_length'], reverse=True)
        }
        
        # JSON 성공 개수 정확하게 계산
        json_success_count = sum(1 for m in successful.values() if m.get('json_parsable', False))
        json_success_rate = json_success_count / len(successful) if successful else 0

        # 통계 계산
        comparison = {
            "fastest_model": rankings['speed'][0][0],
            "fastest_time": rankings['speed'][0][1]['elapsed_time'],
            "cheapest_model": rankings['cost'][0][0],
            "cheapest_cost": rankings['cost'][0][1]['estimated_cost'],
            "most_detailed": rankings['response_length'][0][0],
            "json_success_rate": json_success_rate,
            "json_success_count": json_success_count, 
            "rankings": {
                "speed": [(m, d['elapsed_time']) for m, d in rankings['speed']],
                "cost": [(m, d['estimated_cost']) for m, d in rankings['cost']]
            },
            "total_models_tested": len(results),
            "successful_models": len(successful)
        }
        
        return comparison
    
    def print_comparison(self, comparison: Dict[str, Any]):
        """비교 결과를 보기 좋게 출력"""
        print("\n" + "=" * 80)
        print("📊 비교 분석 결과")
        print("=" * 80)
        
        print(f"\n🏆 가장 빠른 모델: {comparison['fastest_model']} ({comparison['fastest_time']:.2f}s)")
        print(f"💰 가장 저렴한 모델: {comparison['cheapest_model']} (${comparison['cheapest_cost']:.6f})")
        print(f"📝 가장 상세한 응답: {comparison['most_detailed']}")
        print(f"✓ JSON 파싱 성공률: {comparison['json_success_rate']*100:.1f}%")
        
        print("\n📈 속도 순위:")
        for i, (model, time) in enumerate(comparison['rankings']['speed'], 1):
            print(f"  {i}. {model}: {time:.2f}s")
        
        print("\n💵 비용 순위:")
        for i, (model, cost) in enumerate(comparison['rankings']['cost'], 1):
            print(f"  {i}. {model}: ${cost:.6f}")
        
        print("\n" + "=" * 80)
    
    def run_batch_experiments(
        self, 
        prompts: List[str], 
        models: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        여러 프롬프트로 배치 실험
        
        Args:
            prompts (list): 실험할 프롬프트 리스트
            models (list): 실험할 모델 리스트
        
        Returns:
            list: 각 실험 결과 리스트
        """
        print(f"\n🔬 배치 실험 시작: {len(prompts)}개 프롬프트")
        print("=" * 80)
        
        batch_results = []
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n[{i}/{len(prompts)}] 프롬프트 실험 중...")
            result = self.run_experiment(prompt, models)
            batch_results.append(result)
        
        print("\n✅ 배치 실험 완료")
        return batch_results
    
    def get_aggregate_statistics(self) -> Dict[str, Any]:
        """
        전체 실험의 통합 통계
        
        Returns:
            dict: 모델별 평균 성능
        """
        if not self.experiments:
            return {"error": "실험 데이터가 없습니다"}
        
        stats = {}
        
        for exp in self.experiments:
            for model, result in exp['results'].items():
                if not result.get('success', False):
                    continue
                
                if model not in stats:
                    stats[model] = {
                        "total_calls": 0,
                        "total_time": 0,
                        "total_cost": 0,
                        "json_success": 0
                    }
                
                stats[model]['total_calls'] += 1
                stats[model]['total_time'] += result['elapsed_time']
                stats[model]['total_cost'] += result['estimated_cost']

                if result.get('json_parsable', False) is True:
                    stats[model]['json_success'] += 1
            
        # 평균 계산
        aggregate = {}
        for model, data in stats.items():
            calls = data['total_calls']
            aggregate[model] = {
                "total_calls": calls,
                "avg_time": data['total_time'] / calls,
                "avg_cost": data['total_cost'] / calls,
                "json_success_rate": data['json_success'] / calls,
                "json_success_count": data['json_success'] 
            }
        
        return aggregate
    
    def save_experiments(self, filepath: str = "experiments.json"):
        """실험 결과를 파일로 저장"""
        export_data = {
            "total_experiments": len(self.experiments),
            "experiments": self.experiments,
            "aggregate_statistics": self.get_aggregate_statistics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 실험 결과 저장: {filepath}")
    
    def generate_report(self, filepath: str = "experiment_report.md"):
        """
        마크다운 리포트 생성
        """
        stats = self.get_aggregate_statistics()
        
        if "error" in stats:
            print("⚠️ 리포트 생성 실패: 실험 데이터 없음")
            return
        
        report = f"""# LLM 실험 리포트

생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
총 실험 수: {len(self.experiments)}

## 📊 모델별 평균 성능

| 모델 | 호출 수 | 평균 속도 | 평균 비용 | JSON 성공률 |
|------|---------|-----------|-----------|-------------|
"""
        
        for model, data in stats.items():
            report += f"| {model} | {data['total_calls']} | {data['avg_time']:.2f}s | ${data['avg_cost']:.6f} | {data['json_success_rate']*100:.1f}% |\n"
        
        report += "\n## 🏆 종합 평가\n\n"
        
        # 최고 모델 선정
        fastest = min(stats.items(), key=lambda x: x[1]['avg_time'])
        cheapest = min(stats.items(), key=lambda x: x[1]['avg_cost'])
        most_reliable = max(stats.items(), key=lambda x: x[1]['json_success_rate'])
        
        report += f"- **가장 빠른 모델**: {fastest[0]} ({fastest[1]['avg_time']:.2f}s)\n"
        report += f"- **가장 저렴한 모델**: {cheapest[0]} (${cheapest[1]['avg_cost']:.6f})\n"
        report += f"- **가장 안정적인 모델**: {most_reliable[0]} ({most_reliable[1]['json_success_rate']*100:.1f}% 성공률)\n"
        
        report += "\n## 📈 실험 상세\n\n"
        
        for i, exp in enumerate(self.experiments, 1):
            report += f"### 실험 {i}: {exp['experiment_id']}\n\n"
            report += f"**프롬프트**: {exp['prompt'][:100]}...\n\n"
            
            report += "| 모델 | 성공 | 시간 | 비용 |\n"
            report += "|------|------|------|------|\n"
            
            for model, result in exp['results'].items():
                if result.get('success'):
                    report += f"| {model} | ✅ | {result['elapsed_time']:.2f}s | ${result['estimated_cost']:.6f} |\n"
                else:
                    report += f"| {model} | ❌ | - | - |\n"
            
            report += "\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 리포트 생성: {filepath}")


# 싱글톤
_experiment_runner = None

def get_experiment_runner():
    """실험 러너 싱글톤 반환"""
    global _experiment_runner
    if _experiment_runner is None:
        _experiment_runner = ExperimentRunner()
    return _experiment_runner
