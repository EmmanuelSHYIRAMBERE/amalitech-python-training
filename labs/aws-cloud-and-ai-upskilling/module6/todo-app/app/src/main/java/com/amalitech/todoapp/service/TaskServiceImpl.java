package com.amalitech.todoapp.service;

import com.amalitech.todoapp.dto.TaskRequest;
import com.amalitech.todoapp.dto.TaskResponse;
import com.amalitech.todoapp.entity.Task;
import com.amalitech.todoapp.exception.TaskNotFoundException;
import com.amalitech.todoapp.repository.TaskRepository;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TaskServiceImpl implements TaskService {

    private static final String CACHE_NAME = "tasks";

    private final TaskRepository taskRepository;

    public TaskServiceImpl(TaskRepository taskRepository) {
        this.taskRepository = taskRepository;
    }

    @Override
    @Cacheable(value = CACHE_NAME, key = "'all'")
    public List<TaskResponse> getAllTasks() {
        return taskRepository.findAll().stream()
                .map(TaskResponse::from)
                .toList();
    }

    @Override
    @Cacheable(value = CACHE_NAME, key = "#id")
    public TaskResponse getTaskById(Long id) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));
        return TaskResponse.from(task);
    }

    @Override
    @CacheEvict(value = CACHE_NAME, allEntries = true)
    public TaskResponse createTask(TaskRequest request) {
        Task task = new Task();
        task.setTitle(request.getTitle());
        task.setDescription(request.getDescription());
        task.setCompleted(request.isCompleted());
        return TaskResponse.from(taskRepository.save(task));
    }

    @Override
    @CacheEvict(value = CACHE_NAME, allEntries = true)
    public TaskResponse updateTask(Long id, TaskRequest request) {
        Task task = taskRepository.findById(id)
                .orElseThrow(() -> new TaskNotFoundException(id));
        task.setTitle(request.getTitle());
        task.setDescription(request.getDescription());
        task.setCompleted(request.isCompleted());
        return TaskResponse.from(taskRepository.save(task));
    }

    @Override
    @CacheEvict(value = CACHE_NAME, allEntries = true)
    public void deleteTask(Long id) {
        if (!taskRepository.existsById(id)) {
            throw new TaskNotFoundException(id);
        }
        taskRepository.deleteById(id);
    }
}
