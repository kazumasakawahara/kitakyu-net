# Specification: WAM NET Scraper

## ADDED Requirements

### Requirement: WAM NET Data Acquisition
The system SHALL acquire disability welfare facility data from WAM NET (Welfare and Medical Service Network Corporation) for Kitakyushu City.

#### Scenario: Successful data download
- **WHEN** the scraper is executed with target city "Kitakyushu"
- **THEN** CSV files for all service types are downloaded to `data/raw/` directory
- **AND** files are named with timestamp (e.g., `wamnet_kitakyushu_20251031_143022.csv`)

#### Scenario: Multiple service types
- **WHEN** scraper processes all disability service types
- **THEN** data for each service type (生活介護, 就労継続支援A型, 就労継続支援B型, 就労移行支援, etc.) is retrieved
- **AND** each service type data is stored in separate CSV or combined into single file with service_type column

#### Scenario: Data validation
- **WHEN** downloaded CSV data is processed
- **THEN** required columns (事業所名, 法人名, 事業所番号, 所在地, 電話番号, サービス種類) are verified
- **AND** missing columns trigger error with clear message

### Requirement: Error Handling
The system SHALL handle errors gracefully during data acquisition.

#### Scenario: Network error
- **WHEN** network connection fails during download
- **THEN** error is logged with timestamp and error details
- **AND** user receives clear error message
- **AND** partial data is preserved if available

#### Scenario: Invalid data format
- **WHEN** downloaded file has unexpected format
- **THEN** validation error is logged
- **AND** user is notified with specific format issue
- **AND** process continues with other files if multiple downloads

### Requirement: Logging
The system SHALL log all scraper activities for debugging and audit purposes.

#### Scenario: Successful execution logging
- **WHEN** scraper completes successfully
- **THEN** log entry includes: timestamp, files downloaded, record count, execution time
- **AND** log is written to `logs/wamnet_scraper.log`

#### Scenario: Error execution logging
- **WHEN** scraper encounters error
- **THEN** log entry includes: timestamp, error type, error message, stack trace
- **AND** error is categorized (network, validation, file system, etc.)

### Requirement: Configuration
The system SHALL support configuration for scraper behavior.

#### Scenario: Configurable target region
- **WHEN** config.yaml specifies target_city: "北九州市"
- **THEN** only Kitakyushu City data is retrieved
- **AND** other cities are ignored

#### Scenario: Configurable data directory
- **WHEN** config.yaml specifies data_dir: "custom/path"
- **THEN** downloaded files are stored in specified directory
- **AND** directory is created if not exists
