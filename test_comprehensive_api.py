#!/usr/bin/env python3
"""
全面API功能测试脚本
测试所有API端点的功能和性能
"""

import urllib.request
import urllib.parse
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional


class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session_cookies = {}
        self.test_results: Dict[str, Any] = {}
        self.performance_data: List[Dict[str, Any]] = []
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        # 添加cookies
        if self.session_cookies:
            cookie_header = '; '.join([f"{k}={v}" for k, v in self.session_cookies.items()])
            headers['Cookie'] = cookie_header
        
        try:
            start_time = time.time()
            
            if method.upper() == 'GET':
                if data:
                    params = urllib.parse.urlencode(data)
                    url = f"{url}?{params}"
                req = urllib.request.Request(url, headers=headers)
            else:
                if data:
                    data_bytes = json.dumps(data).encode('utf-8')
                else:
                    data_bytes = None
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                duration = time.time() - start_time
                
                # 保存cookies
                if 'Set-Cookie' in response.headers:
                    cookie_str = response.headers['Set-Cookie']
                    for cookie in cookie_str.split(';'):
                        if '=' in cookie:
                            key, value = cookie.strip().split('=', 1)
                            self.session_cookies[key] = value
                
                try:
                    json_data = json.loads(response_data)
                except:
                    json_data = {"raw_response": response_data}
                
                return {
                    'status_code': response.status,
                    'data': json_data,
                    'duration': duration,
                    'success': 200 <= response.status < 300
                }
                
        except Exception as e:
            return {
                'status_code': 0,
                'data': {'error': str(e)},
                'duration': 0,
                'success': False
            }
    
    def test_health_check(self) -> bool:
        """测试健康检查"""
        print("测试健康检查...")
        result = self.make_request('GET', '/health')
        
        if result['success']:
            print(f"  状态: {result['data'].get('status', 'unknown')}")
            print(f"  响应时间: {result['duration']:.3f}s")
            
            # 检查性能数据
            performance = result['data'].get('performance', {})
            if performance:
                print("  性能数据:")
                if 'query_performance' in performance:
                    qp = performance['query_performance']
                    print(f"    查询统计: {qp.get('query_stats', {})}")
                if 'connection_pool' in performance:
                    cp = performance['connection_pool']
                    print(f"    连接池: {cp.get('total_pools', 0)} 个池")
                if 'cache_stats' in performance:
                    cs = performance['cache_stats']
                    print(f"    缓存统计: {cs}")
            
            return True
        else:
            print(f"  健康检查失败: {result['data']}")
            return False
    
    def test_authentication(self) -> bool:
        """测试认证API"""
        print("测试认证API...")
        
        # 测试登录
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        result = self.make_request('POST', '/api/auth/login', login_data)
        
        if result['success']:
            print("  登录成功")
            print(f"  用户: {result['data'].get('user', {}).get('username', 'unknown')}")
            return True
        else:
            print(f"  登录失败: {result['data']}")
            return False
    
    def test_user_management(self) -> bool:
        """测试用户管理API"""
        print("测试用户管理API...")
        
        # 获取用户列表
        result = self.make_request('GET', '/api/users')
        if result['success']:
            users = result['data'].get('users', [])
            print(f"  获取用户列表成功: {len(users)} 个用户")
            
            # 测试创建用户
            new_user = {
                'username': 'test_user',
                'password': 'test123',
                'role': 'agent',
                'shop_id': 1
            }
            create_result = self.make_request('POST', '/api/users', new_user)
            if create_result['success']:
                print("  创建用户成功")
                user_id = create_result['data'].get('id')
                
                # 测试更新用户
                if user_id:
                    update_data = {'role': 'admin'}
                    update_result = self.make_request('PUT', f'/api/users/{user_id}', update_data)
                    if update_result['success']:
                        print("  更新用户成功")
                    else:
                        print(f"  更新用户失败: {update_result['data']}")
                    
                    # 测试删除用户
                    delete_result = self.make_request('DELETE', f'/api/users/{user_id}')
                    if delete_result['success']:
                        print("  删除用户成功")
                    else:
                        print(f"  删除用户失败: {delete_result['data']}")
                
                return True
            else:
                print(f"  创建用户失败: {create_result['data']}")
                return False
        else:
            print(f"  获取用户列表失败: {result['data']}")
            return False
    
    def test_shop_management(self) -> bool:
        """测试店铺管理API"""
        print("测试店铺管理API...")
        
        # 获取店铺列表
        result = self.make_request('GET', '/api/shops')
        if result['success']:
            shops = result['data']
            print(f"  获取店铺列表成功: {len(shops)} 个店铺")
            return True
        else:
            print(f"  获取店铺列表失败: {result['data']}")
            return False
    
    def test_knowledge_base(self) -> bool:
        """测试知识库API"""
        print("测试知识库API...")
        
        # 获取知识库条目
        result = self.make_request('GET', '/api/kb')
        if result['success']:
            items = result['data'].get('items', [])
            print(f"  获取知识库条目成功: {len(items)} 个条目")
            return True
        else:
            print(f"  获取知识库条目失败: {result['data']}")
            return False
    
    def test_messages(self) -> bool:
        """测试消息API"""
        print("测试消息API...")
        
        # 获取消息列表
        result = self.make_request('GET', '/api/messages')
        if result['success']:
            messages = result['data'].get('messages', [])
            print(f"  获取消息列表成功: {len(messages)} 条消息")
            return True
        else:
            print(f"  获取消息列表失败: {result['data']}")
            return False
    
    def test_statistics(self) -> bool:
        """测试统计API"""
        print("测试统计API...")
        
        # 测试日统计
        result = self.make_request('GET', '/api/statistics/daily')
        if result['success']:
            print("  日统计API成功")
        else:
            print(f"  日统计API失败: {result['data']}")
        
        # 测试知识库统计
        result = self.make_request('GET', '/api/statistics/knowledge_base')
        if result['success']:
            print("  知识库统计API成功")
        else:
            print(f"  知识库统计API失败: {result['data']}")
        
        # 测试性能统计
        result = self.make_request('GET', '/api/statistics/performance')
        if result['success']:
            print("  性能统计API成功")
            return True
        else:
            print(f"  性能统计API失败: {result['data']}")
            return False
    
    def test_performance(self, endpoint: str, iterations: int = 10) -> Dict[str, Any]:
        """测试API性能"""
        print(f"测试 {endpoint} 性能 ({iterations} 次)...")
        
        durations = []
        success_count = 0
        
        for i in range(iterations):
            result = self.make_request('GET', endpoint)
            durations.append(result['duration'])
            if result['success']:
                success_count += 1
        
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        success_rate = success_count / iterations
        
        performance_data = {
            'endpoint': endpoint,
            'iterations': iterations,
            'avg_duration': avg_duration,
            'max_duration': max_duration,
            'min_duration': min_duration,
            'success_rate': success_rate,
            'durations': durations
        }
        
        print(f"  平均响应时间: {avg_duration:.3f}s")
        print(f"  最大响应时间: {max_duration:.3f}s")
        print(f"  最小响应时间: {min_duration:.3f}s")
        print(f"  成功率: {success_rate:.2%}")
        
        return performance_data
    
    def run_comprehensive_test(self):
        """运行全面测试"""
        print("开始全面API功能测试...")
        print("=" * 50)
        
        start_time = time.time()
        test_results = {}
        
        # 基础功能测试
        test_results['health_check'] = self.test_health_check()
        test_results['authentication'] = self.test_authentication()
        test_results['user_management'] = self.test_user_management()
        test_results['shop_management'] = self.test_shop_management()
        test_results['knowledge_base'] = self.test_knowledge_base()
        test_results['messages'] = self.test_messages()
        test_results['statistics'] = self.test_statistics()
        
        # 性能测试
        print("\n性能测试...")
        performance_endpoints = [
            '/health',
            '/api/users',
            '/api/shops',
            '/api/kb',
            '/api/messages',
            '/api/statistics/daily'
        ]
        
        for endpoint in performance_endpoints:
            try:
                perf_data = self.test_performance(endpoint, 5)
                self.performance_data.append(perf_data)
            except Exception as e:
                print(f"  性能测试失败 {endpoint}: {e}")
        
        # 总结
        total_time = time.time() - start_time
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        print("\n" + "=" * 50)
        print("测试结果总结:")
        print(f"  总测试时间: {total_time:.2f}s")
        print(f"  通过测试: {passed_tests}/{total_tests}")
        print(f"  成功率: {passed_tests/total_tests:.2%}")
        
        print("\n详细结果:")
        for test_name, result in test_results.items():
            status = "通过" if result else "失败"
            print(f"  {test_name}: {status}")
        
        if self.performance_data:
            print("\n性能数据:")
            for perf in self.performance_data:
                print(f"  {perf['endpoint']}: 平均 {perf['avg_duration']:.3f}s, 成功率 {perf['success_rate']:.2%}")
        
        return {
            'test_results': test_results,
            'performance_data': self.performance_data,
            'summary': {
                'total_time': total_time,
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'success_rate': passed_tests / total_tests
            }
        }


def main():
    """主函数"""
    tester = APITester()
    results = tester.run_comprehensive_test()
    
    # 保存测试结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试结果已保存到: {filename}")


if __name__ == "__main__":
    main()
