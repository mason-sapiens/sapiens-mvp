# Changelog

All notable changes to the Sapiens MVP project.

## [0.2.0] - 2026-02-05

### Changed
- **BREAKING**: Migrated from Anthropic Claude to OpenAI GPT-4o
  - Updated `BaseAgent` to use OpenAI API client
  - Changed environment variable from `ANTHROPIC_API_KEY` to `OPENAI_API_KEY`
  - Updated default model from `claude-sonnet-4-5-20250929` to `gpt-4o`
  - Renamed `call_claude()` to `call_llm()` (backward-compatible alias maintained)

### Added
- `docs/MODEL_CONFIGURATION.md` - Comprehensive guide for model configuration
- `MIGRATION_NOTES.md` - Detailed migration instructions
- `QUICK_REFERENCE.md` - Quick reference card for common tasks
- Support for multiple OpenAI models (GPT-4o, GPT-4 Turbo, GPT-4o Mini)
- Easy configuration for future models (e.g., GPT-5.1)

### Documentation
- Updated all references to use OpenAI instead of Anthropic
- Added model comparison tables
- Included cost optimization strategies
- Updated setup instructions with OpenAI API key requirements

### Migration
- See `MIGRATION_NOTES.md` for complete migration guide
- See `docs/MODEL_CONFIGURATION.md` for model configuration options

## [0.1.0] - 2026-02-05

### Added
- Initial MVP implementation
- Complete multi-agent system with 6 specialized agents
- State machine orchestration with 7 states
- FastAPI REST API with 6 endpoints
- RAG module with ChromaDB integration
- Comprehensive logging module
- 25+ Pydantic schemas for type safety
- Complete documentation suite
- Test framework
- Production-ready architecture

### Agents Implemented
- MainChatAgent - User interface
- ProjectGeneratorAgent - Project design
- ProblemSolutionTutorAgent - Quality evaluation
- ExecutionCoachAgent - Progress tracking
- ReviewerAgent - Artifact review and resume generation

### Features
- Role-aligned project generation
- Problem definition with market/research evaluation
- Solution design with VC/practitioner evaluation
- Milestone-based execution tracking
- Objective artifact review
- Evidence-based resume generation
- Complete audit trail
- RAG-powered knowledge retrieval

### Documentation
- README.md - Project overview
- QUICKSTART.md - 5-minute setup guide
- SYSTEM_OVERVIEW.md - One-page reference
- IMPLEMENTATION_SUMMARY.md - Build summary
- docs/ARCHITECTURE.md - Technical architecture
- docs/API.md - API reference
- docs/DEPLOYMENT.md - Deployment guide

### Infrastructure
- FastAPI application
- Pydantic for data validation
- Structured logging with structlog
- ChromaDB for vector storage
- JSON file persistence (MVP)

---

Format based on [Keep a Changelog](https://keepachangelog.com/)
