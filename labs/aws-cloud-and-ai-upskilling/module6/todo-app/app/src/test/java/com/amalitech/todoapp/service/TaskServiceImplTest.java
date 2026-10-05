package com.amalitech.todoapp.service;

import com.amalitech.todoapp.dto.TaskRequest;
import com.amalitech.todoapp.dto.TaskResponse;
import com.amalitech.todoapp.entity.Task;
import com.amalitech.todoapp.exception.TaskNotFoundException;
import com.amalitech.todoapp.repository.TaskRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class TaskServiceImplTest {

    @Mock
    private TaskRepository taskRepository;

    @InjectMocks
    private TaskServiceImpl taskService;

    private Task task;

    @BeforeEach
    void setUp() {
        task = new Task();
        task.setId(1L);
        task.setTitle("Buy milk");
        task.setDescription("2 liters");
        task.setCompleted(false);
    }

    @Test
    void getAllTasks_returnsMappedResponses() {
        when(taskRepository.findAll()).thenReturn(List.of(task));

        List<TaskResponse> result = taskService.getAllTasks();

        assertThat(result).hasSize(1);
        assertThat(result.get(0).getTitle()).isEqualTo("Buy milk");
    }

    @Test
    void getTaskById_whenFound_returnsResponse() {
        when(taskRepository.findById(1L)).thenReturn(Optional.of(task));

        TaskResponse result = taskService.getTaskById(1L);

        assertThat(result.getId()).isEqualTo(1L);
    }

    @Test
    void getTaskById_whenNotFound_throws() {
        when(taskRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> taskService.getTaskById(99L))
                .isInstanceOf(TaskNotFoundException.class);
    }

    @Test
    void createTask_savesAndReturnsResponse() {
        TaskRequest request = new TaskRequest();
        request.setTitle("New task");
        when(taskRepository.save(any(Task.class))).thenReturn(task);

        TaskResponse result = taskService.createTask(request);

        assertThat(result.getTitle()).isEqualTo("Buy milk");
        verify(taskRepository).save(any(Task.class));
    }

    @Test
    void deleteTask_whenNotFound_throws() {
        when(taskRepository.existsById(42L)).thenReturn(false);

        assertThatThrownBy(() -> taskService.deleteTask(42L))
                .isInstanceOf(TaskNotFoundException.class);
    }
}
