# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]

### Changed

### TBD
- finish adding the link in the email to validate the modifications

### Added
- New mode for employees planning
  - new constraints (week-ends, consecutive working hours/days, etc.)
  - batch of weeks
- Modification proposal sent via email

### Changed
- front-end: dispatch week/day management in js files
- back-end refactoring: all model attributes in english

### TBD
- right permissions in TTapp/views

## [0.3.0] - 2019-11-07
### Added
- Holidays in solver
- New preferences mode
- More preferences for tutors
- Side panel in main view:
  - Work copy selection
  - Swap versions
  - Reassign rooms
- Side panel in default week view:
  - Change someone else default week
  - Set preferences for each course type, per training programme
- Proposals and transparency checks when course dragging

### Changed
- Bug fixes (slots, rights)
- Import improved


## [0.2.1] - 2019-07-18
### Added
- Import process:
  - Interface for superusers
  - Pattern configuration file
  - Pattern planification file generation
- Multi-department constraints in the solver

### Changed
- Logo/case


## [0.2.0] - 2019-02-04
### Added
- Multi-department support
- Solve board improvements:
  - Associated constraints selection
  - Stabilization option based on previous resolution
  - Solver option for production environment
- Satistics view display basic information concerning rooms and tutors

### Changed
- Solver logs are displayed in a fixed size area
- Docker support improvment


## [0.1] - 2018-11-06
### Added
- Initial features
