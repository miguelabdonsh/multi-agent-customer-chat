# Test Suite - Multi-Agent Customer Chat

This directory contains comprehensive tests for the Multi-Agent Customer Chat system.

## Test Structure

### Core Test Files

- **`test_infrastructure.py`** - Infrastructure and connectivity tests
- **`test_agents.py`** - Individual agent functionality tests
- **`test_workflow_integration.py`** - Complete LangGraph workflow tests
- **`test_cache_database.py`** - Redis cache and database integration tests
- **`test_guardrails.py`** - Content safety and validation tests
- **`run_all_tests.py`** - Main test runner that executes all test suites

## Test Categories

### 1. Infrastructure Tests (`test_infrastructure.py`)
- Health check endpoints
- WebSocket connectivity
- Session creation and management
- Basic API functionality

### 2. Agent Tests (`test_agents.py`)
- **Router Agent**: Intent classification and routing
- **FAQ Agent**: Knowledge base queries and responses
- **Support Agent**: Technical assistance scenarios
- **Escalation Agent**: Urgent request handling
- **Guardrails Agent**: Content safety validation

### 3. Workflow Integration Tests (`test_workflow_integration.py`)
- Complete LangGraph workflow execution
- FAQ scenarios with knowledge base
- Support scenarios with technical issues
- Escalation scenarios with urgent requests
- Multi-turn conversation flows

### 4. Cache & Database Tests (`test_cache_database.py`)
- Redis cache functionality
- Database connectivity and queries
- Knowledge base integration
- Cache performance validation
- Session state persistence

### 5. Guardrails Tests (`test_guardrails.py`)
- Safe content validation
- Unsafe content detection
- Hallucination detection
- Edge case handling
- Security validation

## Running Tests

### Run All Tests
```bash
cd backend/test
python run_all_tests.py
```

### Run Individual Test Suites
```bash
# Infrastructure tests
python test_infrastructure.py

# Agent tests
python test_agents.py

# Workflow integration tests
python test_workflow_integration.py

# Cache and database tests
python test_cache_database.py

# Guardrails tests
python test_guardrails.py
```

### Get Help
```bash
python run_all_tests.py --help
```

## Test Execution Order

The main test runner executes tests in the following order:

1. **Infrastructure Tests** - Verify basic system connectivity
2. **Cache & Database Tests** - Validate data layer functionality
3. **Agent Tests** - Test individual agent components
4. **Guardrails Tests** - Validate content safety mechanisms
5. **Workflow Integration Tests** - Test complete system integration

## Test Results

Each test suite provides:
- ✅/❌ Pass/Fail status for each test
- Detailed error messages for failures
- Performance metrics (execution time)
- Summary reports with overall results

## Prerequisites

Before running tests, ensure:
- Docker containers are running (`docker compose up`)
- Backend service is accessible on `localhost:8000`
- Database and Redis are properly initialized
- All dependencies are installed

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure Docker containers are running
2. **Import Errors**: Check that backend path is correctly set
3. **Timeout Errors**: Increase timeout values for slow environments
4. **Database Errors**: Verify database initialization and connectivity

### Debug Mode

For detailed debugging, run individual test files with verbose output:
```bash
python -u test_infrastructure.py
```

## Test Coverage

The test suite covers:
- ✅ All agent types (Router, FAQ, Support, Escalation, Guardrails)
- ✅ Complete workflow integration
- ✅ Database and cache functionality
- ✅ Content safety and validation
- ✅ Error handling and edge cases
- ✅ Performance and scalability aspects

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Include comprehensive error handling
3. Add clear test descriptions
4. Update this README if adding new test categories
5. Ensure tests are independent and can run in any order 