# LEO AI Assistant - Test Plans for New Features

## Overview
This document outlines comprehensive test plans for the new features planned for LEO AI Assistant. The tests cover functionality, performance, security, and compatibility aspects.

## Test Strategy

### 1. Test Levels
- **Unit Tests**: Test individual functions and modules
- **Integration Tests**: Test interactions between modules
- **System Tests**: Test end-to-end functionality
- **Performance Tests**: Test system performance and scalability
- **Security Tests**: Test safety and security aspects

### 2. Test Frameworks
- **Pytest** for unit and integration testing
- **Locust** for performance testing
- **Custom security validation** using existing safety system

### 3. Test Environment
- Terminal mode (primary focus)
- GUI mode (regression testing)
- Daemon mode (background processing)

## Phase 1 - High Priority Features

### Feature 1: File Management System

**Test File**: `Tests/test_file_management.py`

**Unit Tests**:
```python
import pytest
from Backend.Actions.Files import (
    OpenFile, EditFile, ReadFile, CreateFile, DeleteFile,
    CopyFile, MoveFile, RenameFile, ListFiles, FileInfo
)
import os
import tempfile
import shutil

class TestFileManagement:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_create_file(self, temp_dir):
        test_file = os.path.join(temp_dir, "test.txt")
        CreateFile(f"{test_file}|Hello, World!")
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            assert f.read() == "Hello, World!"
    
    def test_read_file(self, temp_dir):
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        content = ReadFile(test_file)
        assert content == "Test content"
    
    def test_delete_file(self, temp_dir):
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test")
        DeleteFile(test_file)
        assert not os.path.exists(test_file)
    
    def test_list_files(self, temp_dir):
        file1 = os.path.join(temp_dir, "file1.txt")
        file2 = os.path.join(temp_dir, "file2.txt")
        with open(file1, 'w') as f:
            f.write("Test1")
        with open(file2, 'w') as f:
            f.write("Test2")
        files = ListFiles(temp_dir)
        assert "file1.txt" in files
        assert "file2.txt" in files
    
    def test_file_info(self, temp_dir):
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("Test content")
        info = FileInfo(test_file)
        assert info.st_size > 0
```

**Integration Tests**:
```python
def test_file_operations_workflow(temp_dir):
    # Create file
    test_file = os.path.join(temp_dir, "test.txt")
    CreateFile(f"{test_file}|Initial content")
    assert os.path.exists(test_file)
    
    # Read file
    content = ReadFile(test_file)
    assert content == "Initial content"
    
    # List files
    files = ListFiles(temp_dir)
    assert "test.txt" in files
```

### Feature 2: System Monitoring

**Test File**: `Tests/test_system_monitor.py`

**Unit Tests**:
```python
import pytest
from Backend.Actions.SystemMonitor import (
    get_cpu_usage, get_memory_usage, get_disk_usage,
    get_network_activity, get_battery_status
)

class TestSystemMonitor:
    def test_cpu_usage(self):
        cpu = get_cpu_usage()
        assert isinstance(cpu, float)
        assert 0 <= cpu <= 100
    
    def test_memory_usage(self):
        memory = get_memory_usage()
        assert isinstance(memory, float)
        assert 0 <= memory <= 100
    
    def test_disk_usage(self):
        disk = get_disk_usage()
        assert isinstance(disk, float)
        assert 0 <= disk <= 100
    
    def test_battery_status(self):
        battery = get_battery_status()
        assert isinstance(battery, dict)
        assert 'percent' in battery or 'charging' in battery
    
    def test_network_activity(self):
        network = get_network_activity()
        assert isinstance(network, dict)
        assert 'sent' in network
        assert 'received' in network
```

**Performance Tests**:
```python
def test_monitor_performance():
    # Test that monitoring functions don't block
    import time
    start = time.time()
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()
    duration = time.time() - start
    assert duration < 1.0  # Should respond in under 1 second
```

### Feature 3: Music Control System

**Test File**: `Tests/test_music_control.py`

**Unit Tests**:
```python
import pytest
from Backend.Actions.Music import (
    play_music, pause_music, stop_music,
    next_track, previous_track, set_volume
)

class TestMusicControl:
    def test_play_music(self):
        result = play_music()
        assert result in ["Playing", "Already playing", "No media player found"]
    
    def test_pause_music(self):
        result = pause_music()
        assert result in ["Paused", "Already paused", "No media player found"]
    
    def test_stop_music(self):
        result = stop_music()
        assert result in ["Stopped", "Not playing", "No media player found"]
    
    def test_volume_control(self):
        result = set_volume(50)
        assert result in ["Volume set to 50%", "Failed to set volume"]
    
    def test_track_navigation(self):
        next_result = next_track()
        prev_result = previous_track()
        assert isinstance(next_result, str)
        assert isinstance(prev_result, str)
```

### Feature 4: Enhanced Task Management

**Test File**: `Tests/test_task_management.py`

**Unit Tests**:
```python
import pytest
from Backend.app.tasks import (
    create_task, edit_task, delete_task,
    get_tasks, complete_task, get_task_statistics
)

class TestTaskManagement:
    @pytest.fixture
    def test_task(self):
        task_id = create_task("Test task", "High", "2024-12-31")
        yield task_id
        try:
            delete_task(task_id)
        except:
            pass
    
    def test_create_task(self):
        task_id = create_task("New task", "Medium", "2024-12-31")
        assert task_id is not None
        tasks = get_tasks()
        assert any(task['id'] == task_id for task in tasks)
        delete_task(task_id)
    
    def test_edit_task(self, test_task):
        edit_task(test_task, "Updated task", "Low", "2025-01-01")
        tasks = get_tasks()
        task = next(t for t in tasks if t['id'] == test_task)
        assert task['title'] == "Updated task"
        assert task['priority'] == "Low"
    
    def test_complete_task(self, test_task):
        complete_task(test_task)
        tasks = get_tasks()
        task = next(t for t in tasks if t['id'] == test_task)
        assert task['completed'] == True
    
    def test_task_statistics(self, test_task):
        stats = get_task_statistics()
        assert isinstance(stats['total'], int)
        assert isinstance(stats['completed'], int)
        assert isinstance(stats['pending'], int)
        assert stats['total'] == stats['completed'] + stats['pending']
```

### Feature 5: Advanced Weather System

**Test File**: `Tests/test_advanced_weather.py`

**Unit Tests**:
```python
import pytest
from Backend.app.weather import (
    get_current_weather, get_weather_forecast,
    get_hourly_forecast, get_weather_alerts
)

class TestAdvancedWeather:
    def test_current_weather(self):
        weather = get_current_weather("Hyderabad")
        assert isinstance(weather, dict)
        assert 'temperature' in weather
        assert 'humidity' in weather
        assert 'wind_speed' in weather
    
    def test_forecast(self):
        forecast = get_weather_forecast("Hyderabad", 5)
        assert isinstance(forecast, list)
        assert len(forecast) <= 5
        if forecast:
            assert 'date' in forecast[0]
            assert 'temperature' in forecast[0]
    
    def test_hourly_forecast(self):
        hourly = get_hourly_forecast("Hyderabad", 12)
        assert isinstance(hourly, list)
        assert len(hourly) <= 12
    
    def test_weather_alerts(self):
        alerts = get_weather_alerts("Hyderabad")
        assert isinstance(alerts, list)
```

## Phase 2 - Medium Priority Features

### Feature 6: Email Integration

**Test File**: `Tests/test_email_integration.py`

**Unit Tests**:
```python
import pytest
from Backend.app.email import (
    configure_email_account, get_unread_emails,
    send_email, search_emails, mark_email_read
)

class TestEmailIntegration:
    def test_configuration(self):
        result = configure_email_account("test@example.com", "password")
        assert result in ["Configured successfully", "Invalid credentials"]
    
    def test_get_unread_emails(self):
        emails = get_unread_emails()
        assert isinstance(emails, list)
    
    def test_send_email(self):
        result = send_email("recipient@example.com", "Test Subject", "Test Body")
        assert result in ["Email sent successfully", "Failed to send email"]
    
    def test_search_emails(self):
        results = search_emails("Test subject")
        assert isinstance(results, list)
```

### Feature 7: Calendar Management

**Test File**: `Tests/test_calendar_management.py`

**Unit Tests**:
```python
import pytest
from Backend.app.calendar import (
    create_event, get_events, edit_event,
    delete_event, get_upcoming_events
)

class TestCalendarManagement:
    def test_create_event(self):
        event_id = create_event("Team Meeting", "2024-12-31 14:00", "2024-12-31 15:00")
        assert event_id is not None
    
    def test_get_events(self):
        events = get_events("2024-12-01", "2024-12-31")
        assert isinstance(events, list)
    
    def test_upcoming_events(self):
        upcoming = get_upcoming_events(7)  # Next 7 days
        assert isinstance(upcoming, list)
```

### Feature 8: News and Information Service

**Test File**: `Tests/test_news_service.py`

**Unit Tests**:
```python
import pytest
from Backend.app.news import (
    get_news_by_category, search_news,
    get_top_headlines, set_news_preferences
)

class TestNewsService:
    def test_get_top_headlines(self):
        headlines = get_top_headlines()
        assert isinstance(headlines, list)
    
    def test_news_by_category(self):
        tech_news = get_news_by_category("technology")
        assert isinstance(tech_news, list)
    
    def test_search_news(self):
        results = search_news("AI assistant")
        assert isinstance(results, list)
```

### Feature 9: Translation Services

**Test File**: `Tests/test_translation.py`

**Unit Tests**:
```python
import pytest
from Backend.app.translate import (
    translate_text, detect_language,
    get_translation_history, clear_translation_history
)

class TestTranslationServices:
    def test_translate_text(self):
        result = translate_text("Hello, world!", "es")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_detect_language(self):
        language = detect_language("Bonjour le monde")
        assert isinstance(language, str)
        assert len(language) <= 2
    
    def test_translation_history(self):
        history = get_translation_history()
        assert isinstance(history, list)
```

### Feature 10: Enhanced Clipboard Management

**Test File**: `Tests/test_clipboard.py`

**Unit Tests**:
```python
import pytest
from Backend.app.clipboard import (
    copy_to_clipboard, paste_from_clipboard,
    get_clipboard_history, clear_clipboard_history
)

class TestClipboardManagement:
    def test_copy_paste(self):
        test_text = "Test clipboard content"
        copy_to_clipboard(test_text)
        pasted = paste_from_clipboard()
        assert pasted == test_text
    
    def test_clipboard_history(self):
        copy_to_clipboard("First item")
        copy_to_clipboard("Second item")
        history = get_clipboard_history()
        assert isinstance(history, list)
        assert len(history) >= 2
```

## Phase 3 - Advanced Features

### Feature 11: Multi-language Support

**Test File**: `Tests/test_multi_language.py`

**Unit Tests**:
```python
import pytest
from Backend.LanguageDetection import (
    detect_language, translate_response,
    set_language_preference
)

class TestMultiLanguageSupport:
    def test_language_detection(self):
        language = detect_language("Bonjour le monde")
        assert language == "fr"
    
    def test_translate_response(self):
        translated = translate_response("Hello", "es")
        assert translated == "Hola"
    
    def test_language_preference(self):
        set_language_preference("es")
        assert get_language_preference() == "es"
```

### Feature 12: Context Awareness

**Test File**: `Tests/test_context_awareness.py`

**Unit Tests**:
```python
import pytest
from Backend.Memory import (
    add_to_context, get_context, clear_context,
    get_contextual_response
)

class TestContextAwareness:
    def test_add_to_context(self):
        add_to_context("user", "What's the weather in Hyderabad?")
        add_to_context("assistant", "It's sunny and 30°C")
        context = get_context()
        assert len(context) == 2
    
    def test_contextual_response(self):
        add_to_context("user", "What's the weather in Hyderabad?")
        add_to_context("assistant", "It's sunny and 30°C")
        response = get_contextual_response("Is it going to rain?")
        assert "rain" in response.lower()
```

### Feature 13: User Personalization

**Test File**: `Tests/test_personalization.py`

**Unit Tests**:
```python
import pytest
from Backend.Personalization import (
    create_user_profile, update_user_preference,
    get_user_preferences, get_personalized_response
)

class TestPersonalization:
    def test_create_profile(self):
        profile_id = create_user_profile("test_user")
        assert profile_id is not None
    
    def test_update_preference(self):
        update_user_preference("test_user", "news_category", "technology")
        preferences = get_user_preferences("test_user")
        assert preferences.get("news_category") == "technology"
```

### Feature 14: Smart Home Integration

**Test File**: `Tests/test_smarthome.py`

**Unit Tests**:
```python
import pytest
from Backend.app.smarthome import (
    discover_devices, control_device,
    get_device_status, create_scene
)

class TestSmartHomeIntegration:
    def test_discover_devices(self):
        devices = discover_devices()
        assert isinstance(devices, list)
    
    def test_device_control(self):
        result = control_device("light_1", "on")
        assert result in ["Success", "Device not found", "Failed to control"]
    
    def test_device_status(self):
        status = get_device_status("light_1")
        assert isinstance(status, dict)
        assert 'status' in status
```

### Feature 15: Extensibility Framework

**Test File**: `Tests/test_plugins.py`

**Unit Tests**:
```python
import pytest
from Backend.PluginSystem import (
    load_plugins, get_available_plugins,
    enable_plugin, disable_plugin, execute_plugin_command
)

class TestPluginSystem:
    def test_load_plugins(self):
        plugins = load_plugins()
        assert isinstance(plugins, list)
    
    def test_plugin_management(self):
        available = get_available_plugins()
        if available:
            enable_result = enable_plugin(available[0])
            assert enable_result == "Success"
            disable_result = disable_plugin(available[0])
            assert disable_result == "Success"
```

## System Integration Tests

**Test File**: `Tests/test_system_integration.py`

```python
import pytest
import subprocess
import time

class TestSystemIntegration:
    def test_terminal_mode_startup(self):
        # Test that LEO starts successfully in terminal mode
        result = subprocess.run(['python', 'Main.py', '--terminal', '--test'], 
                             capture_output=True, text=True, timeout=10)
        assert "Listening for hotword:" in result.stdout
    
    def test_command_recognition(self):
        # Test that basic commands are recognized
        from Backend.Model import FirstLayerDMM
        command = FirstLayerDMM("open notepad")
        assert command == ["open notepad"]
    
    def test_safety_system(self):
        # Test safety validation
        from Backend.Safety import ValidateCommand
        safe_result = ValidateCommand("open notepad")
        dangerous_result = ValidateCommand("delete system32")
        assert safe_result['safe'] == True
        assert dangerous_result['safe'] == False
```

## Performance Tests

**Test File**: `Tests/test_performance.py`

```python
import pytest
import time

class TestPerformance:
    def test_response_time(self):
        # Test that LEO responds quickly to commands
        from Backend.Model import FirstLayerDMM
        start = time.time()
        for _ in range(100):
            FirstLayerDMM("open notepad")
        duration = time.time() - start
        assert duration < 0.5  # 100 commands in under 0.5 seconds
    
    def test_memory_usage(self):
        # Test that memory usage stays within acceptable limits
        import psutil
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # Perform some operations
        from Backend.Model import FirstLayerDMM
        for _ in range(1000):
            FirstLayerDMM("open notepad")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        assert final_memory - initial_memory < 50  # Shouldn't use more than 50MB
```

## Security Tests

**Test File**: `Tests/test_security.py`

```python
import pytest

class TestSecurity:
    def test_dangerous_commands(self):
        from Backend.Safety import ValidateCommand
        commands = [
            "delete system32",
            "format c:",
            "shutdown -f -t 0",
            "rm -rf /"
        ]
        
        for cmd in commands:
            result = ValidateCommand(cmd)
            assert result['safe'] == False
            assert result['requires_confirmation'] == True
    
    def test_safe_commands(self):
        from Backend.Safety import ValidateCommand
        commands = [
            "open notepad",
            "what's the weather today",
            "play music",
            "write a note"
        ]
        
        for cmd in commands:
            result = ValidateCommand(cmd)
            assert result['safe'] == True
            assert result['requires_confirmation'] == False
```

## Test Execution

### Running Tests
```bash
# Run all tests
pytest Tests/

# Run specific feature tests
pytest Tests/test_file_management.py -v
pytest Tests/test_system_monitor.py -v

# Run tests with coverage
pytest Tests/ --cov=Backend --cov-report=html

# Run performance tests
pytest Tests/test_performance.py -v -xvs
```

### Test Reporting
```bash
# Generate detailed test report
pytest Tests/ -v --tb=short --junitxml=test_results.xml

# Generate coverage report
pytest Tests/ --cov=Backend --cov-report=html --cov-report=xml
```

## Regression Testing

### Critical Path Tests
1. Terminal mode startup and operation
2. GUI mode fallback functionality
3. Safety system validation
4. PID control and single-instance execution
5. Logging system functionality
6. Audio system (TTS, STT, hotword detection)

### Smoke Tests
```python
# Run smoke tests before each release
pytest Tests/test_system_integration.py Tests/test_security.py -v
```

## Test Maintenance

### Test Data Management
- Use temporary directories for file operations
- Clean up test files after each test
- Use mock data for external API calls
- Implement retry logic for flaky tests

### Test Environment
- Test on different OS platforms (Windows, macOS, Linux)
- Test with different Python versions
- Test in different network conditions (online/offline)

## Conclusion

These test plans provide comprehensive coverage for all new features, ensuring that LEO AI Assistant remains reliable, secure, and performant as it evolves. The tests are designed to be repeatable, maintainable, and provide quick feedback on the system's health.
