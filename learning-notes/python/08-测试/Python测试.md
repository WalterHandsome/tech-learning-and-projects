# Python测试

## 1. 测试概述

测试是软件开发的重要环节，Python提供了多种测试框架：
- **unittest**：Python标准库中的测试框架
- **pytest**：功能强大的第三方测试框架
- **doctest**：文档测试
- **nose2**：unittest的扩展

## 2. unittest框架

### 2.1 基本使用

```python
import unittest

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
    
    def test_subtract(self):
        self.assertEqual(3 - 1, 2)
    
    def test_multiply(self):
        self.assertEqual(2 * 3, 6)
    
    def test_divide(self):
        self.assertEqual(6 / 2, 3)

if __name__ == '__main__':
    unittest.main()
```

### 2.2 断言方法

```python
import unittest

class TestAssertions(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(1, 1)
        self.assertNotEqual(1, 2)
    
    def test_true_false(self):
        self.assertTrue(True)
        self.assertFalse(False)
    
    def test_is_none(self):
        self.assertIsNone(None)
        self.assertIsNotNone(1)
    
    def test_in(self):
        self.assertIn(1, [1, 2, 3])
        self.assertNotIn(4, [1, 2, 3])
    
    def test_is_instance(self):
        self.assertIsInstance(1, int)
        self.assertNotIsInstance('1', int)
    
    def test_almost_equal(self):
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)
    
    def test_regex(self):
        self.assertRegex('hello world', r'hello')
        self.assertNotRegex('hello world', r'goodbye')
```

### 2.3 测试装置（Fixture）

```python
import unittest

class TestFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """类级别的设置，在所有测试方法执行前执行一次"""
        print('setUpClass')
        cls.shared_resource = 'shared'
    
    @classmethod
    def tearDownClass(cls):
        """类级别的清理，在所有测试方法执行后执行一次"""
        print('tearDownClass')
    
    def setUp(self):
        """方法级别的设置，在每个测试方法执行前执行"""
        print('setUp')
        self.data = [1, 2, 3]
    
    def tearDown(self):
        """方法级别的清理，在每个测试方法执行后执行"""
        print('tearDown')
    
    def test_example(self):
        print('test_example')
        self.assertEqual(len(self.data), 3)
```

### 2.4 跳过测试

```python
import unittest
import sys

class TestSkip(unittest.TestCase):
    @unittest.skip('跳过这个测试')
    def test_skip(self):
        self.fail('不应该执行')
    
    @unittest.skipIf(sys.platform == 'win32', 'Windows平台跳过')
    def test_skip_if(self):
        pass
    
    @unittest.skipUnless(sys.platform == 'linux', '非Linux平台跳过')
    def test_skip_unless(self):
        pass
```

### 2.5 测试套件

```python
import unittest

class TestA(unittest.TestCase):
    def test_a(self):
        self.assertTrue(True)

class TestB(unittest.TestCase):
    def test_b(self):
        self.assertTrue(True)

# 创建测试套件
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestA('test_a'))
    suite.addTest(TestB('test_b'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
```

## 3. pytest框架

### 3.1 安装

```bash
pip install pytest
```

### 3.2 基本使用

```python
# test_math.py
def test_add():
    assert 1 + 1 == 2

def test_subtract():
    assert 3 - 1 == 2

# 运行测试
# pytest test_math.py
```

### 3.3 测试类

```python
class TestMath:
    def test_add(self):
        assert 1 + 1 == 2
    
    def test_multiply(self):
        assert 2 * 3 == 6
```

### 3.4 装置（Fixture）

```python
import pytest

@pytest.fixture
def sample_data():
    """装置函数，返回测试数据"""
    return [1, 2, 3]

def test_with_fixture(sample_data):
    """使用装置"""
    assert len(sample_data) == 3
    assert sample_data[0] == 1

@pytest.fixture(scope='module')
def shared_resource():
    """模块级别的装置"""
    print('setup')
    yield 'resource'
    print('teardown')

def test_1(shared_resource):
    assert shared_resource == 'resource'

def test_2(shared_resource):
    assert shared_resource == 'resource'
```

### 3.5 参数化测试

```python
import pytest

@pytest.mark.parametrize('a, b, expected', [
    (1, 1, 2),
    (2, 3, 5),
    (5, 5, 10),
])
def test_add(a, b, expected):
    assert a + b == expected
```

### 3.6 标记和跳过

```python
import pytest

@pytest.mark.slow
def test_slow():
    """标记为慢速测试"""
    import time
    time.sleep(1)
    assert True

@pytest.mark.skip(reason='跳过这个测试')
def test_skip():
    assert False

@pytest.mark.skipif(sys.platform == 'win32', reason='Windows平台跳过')
def test_skip_if():
    assert True
```

### 3.7 异常测试

```python
import pytest

def test_exception():
    with pytest.raises(ValueError):
        int('not a number')

def test_exception_message():
    with pytest.raises(ValueError, match='invalid literal'):
        int('not a number')
```

## 4. Mock和Stub

### 4.1 unittest.mock

```python
from unittest.mock import Mock, MagicMock, patch

# 创建Mock对象
mock_obj = Mock()
mock_obj.method.return_value = 'result'
assert mock_obj.method() == 'result'

# 验证调用
mock_obj.method.assert_called_once()

# 使用patch装饰器
@patch('module.function')
def test_with_patch(mock_function):
    mock_function.return_value = 'mocked'
    result = module.function()
    assert result == 'mocked'
```

### 4.2 pytest-mock

```python
import pytest

def test_with_mock(mocker):
    # 创建Mock对象
    mock_func = mocker.patch('module.function')
    mock_func.return_value = 'mocked'
    
    result = module.function()
    assert result == 'mocked'
    mock_func.assert_called_once()
```

## 5. 测试覆盖率

### 5.1 安装coverage

```bash
pip install coverage
```

### 5.2 使用coverage

```bash
# 运行测试并收集覆盖率
coverage run -m pytest

# 生成报告
coverage report

# 生成HTML报告
coverage html
```

### 5.3 pytest-cov插件

```bash
pip install pytest-cov

# 运行测试并显示覆盖率
pytest --cov=module --cov-report=html
```

## 6. 测试最佳实践

### 6.1 测试结构

```
project/
├── src/
│   └── module.py
└── tests/
    ├── __init__.py
    ├── test_module.py
    └── conftest.py
```

### 6.2 测试命名

```python
# 好的命名
def test_user_login_success():
    pass

def test_user_login_failure():
    pass

# 不好的命名
def test1():
    pass

def test_login():
    pass
```

### 6.3 测试独立性

```python
# 好的做法：每个测试独立
def test_add():
    assert 1 + 1 == 2

def test_subtract():
    assert 3 - 1 == 2

# 不好的做法：测试之间依赖
class TestDependent:
    def test_first(self):
        self.value = 1
    
    def test_second(self):
        # 依赖test_first的结果
        assert self.value == 1
```

### 6.4 测试数据

```python
# 使用装置提供测试数据
@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'test@example.com'
    }

def test_create_user(user_data):
    user = create_user(user_data)
    assert user.username == 'testuser'
```

## 7. 集成测试

### 7.1 测试API

```python
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello World'}

def test_create_item():
    response = client.post('/items/', json={'name': 'test'})
    assert response.status_code == 200
    assert response.json()['name'] == 'test'
```

### 7.2 测试数据库

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Base, User

@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_user(db_session):
    user = User(username='test', email='test@example.com')
    db_session.add(user)
    db_session.commit()
    
    found = db_session.query(User).filter_by(username='test').first()
    assert found is not None
    assert found.email == 'test@example.com'
```

## 8. 性能测试

### 8.1 使用timeit

```python
import timeit

def slow_function():
    time.sleep(0.1)

# 测量执行时间
time = timeit.timeit(slow_function, number=10)
print(f'平均时间: {time / 10}秒')
```

### 8.2 pytest-benchmark

```bash
pip install pytest-benchmark
```

```python
def test_performance(benchmark):
    result = benchmark(slow_function)
    assert result is not None
```

## 9. 持续集成

### 9.1 GitHub Actions示例

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 10. 总结

Python测试工具：
- **unittest**：Python标准库，适合简单测试
- **pytest**：功能强大，适合复杂项目
- **coverage**：测试覆盖率工具
- **mock**：模拟对象，用于单元测试

编写良好的测试可以提高代码质量和可维护性。

