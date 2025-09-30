# Contributing to OpenWebUI Engine

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Docker (optional, for testing container builds)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Viss007/openwebui-with-engine.git
   cd openwebui-with-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**
   ```bash
   uvicorn engine.engine_server:app --host 0.0.0.0 --port 8080 --reload
   ```

5. **Test your changes**
   ```bash
   # Syntax check
   python -m py_compile engine/*.py
   
   # Import verification
   python -c "from engine import engine_server, task_api, task_runner, engine_daemon"
   
   # Docker build test
   docker build -t openwebui-engine:test .
   ```

## Code Standards

### Python Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

### API Route Organization

All API endpoints should be organized under the `/api/*` pattern:

- ✅ Good: `/api/chat`, `/api/mode`, `/api/history/{id}`
- ❌ Avoid: `/chat`, `/mode`, `/history/{id}` (unless backward compatibility aliases)

For backward compatibility, maintain legacy route aliases:

```python
@app.get("/api/endpoint")
def new_endpoint():
    """Primary endpoint"""
    return {...}

@app.get("/endpoint")
def legacy_endpoint():
    """Legacy alias - use /api/endpoint instead"""
    return new_endpoint()
```

### Environment Variables

All configuration must use environment variables (never hardcode):

- Document new variables in `.env.example`
- Provide sensible defaults for optional settings
- Use descriptive names with project prefix (e.g., `ENGINE_LOG_LEVEL`)

## Making Changes

### Before You Start

1. Check existing issues and PRs to avoid duplicates
2. Create an issue for significant changes to discuss the approach
3. Fork the repository and create a feature branch

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Follow the coding standards above
   - Add tests if applicable

3. **Test locally**
   ```bash
   # Start server and test manually
   uvicorn engine.engine_server:app --reload
   
   # Test key endpoints
   curl http://localhost:8080/healthz
   curl http://localhost:8080/api/mode
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

   Use conventional commit messages:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation only
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

5. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Process

1. **Fill out the PR template** completely
2. **Ensure all CI checks pass**:
   - Python syntax validation
   - Import verification
   - Docker build
3. **Link related issues** using `Fixes #123` or `Relates to #123`
4. **Request review** from maintainers
5. **Address feedback** promptly and professionally

## Testing Guidelines

### Manual Testing

Key endpoints to test:

```bash
# Health checks
curl http://localhost:8080/healthz
curl http://localhost:8080/engine/ready

# API endpoints
curl http://localhost:8080/api/mode
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"test","session_identifier":"test"}'

# Task API
curl http://localhost:8080/engine/tasks/list
```

### Docker Testing

Always test Docker builds before submitting:

```bash
docker build -t openwebui-engine:test .
docker run -p 8080:8080 -e OPENAI_API_KEY=test openwebui-engine:test
```

## Task Runner Extensions

To add new tasks to the task runner:

```python
# In engine/task_runner.py or your module
from engine import task_runner

@task_runner.register('my_task')
def my_task(**kwargs):
    """Task description"""
    param1 = kwargs.get('param1', 'default')
    # Task logic here
    return {'status': 'success', 'result': param1}
```

Test via API:

```bash
curl -X POST http://localhost:8080/engine/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"name":"my_task","args":{"param1":"value"}}'
```

## Documentation

- Update README.md for user-facing changes
- Update .env.example for new environment variables
- Add inline comments for complex logic
- Update API documentation if endpoints change

## Questions or Problems?

- Open an issue for bugs or feature requests
- Tag maintainers for urgent matters
- Be respectful and constructive in all communications

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help others learn and grow

Thank you for contributing to OpenWebUI Engine! 🚀
