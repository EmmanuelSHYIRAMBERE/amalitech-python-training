package com.amalitech.todoapp.service;

import com.amalitech.todoapp.dto.TaskRequest;
import com.amalitech.todoapp.dto.TaskResponse;

import java.util.List;

public interface TaskService {

    List<TaskResponse> getAllTasks();

    TaskResponse getTaskById(Long id);

    TaskResponse createTask(TaskRequest request);

    TaskResponse updateTask(Long id, TaskRequest request);

    void deleteTask(Long id);
}
