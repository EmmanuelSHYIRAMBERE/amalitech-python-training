package com.amalitech.todoapp.dto;

import com.amalitech.todoapp.entity.Task;

import java.io.Serializable;
import java.time.Instant;

public class TaskResponse implements Serializable {

    private Long id;
    private String title;
    private String description;
    private boolean completed;
    private Instant createdAt;
    private Instant updatedAt;

    public TaskResponse() {
    }

    public static TaskResponse from(Task task) {
        TaskResponse response = new TaskResponse();
        response.id = task.getId();
        response.title = task.getTitle();
        response.description = task.getDescription();
        response.completed = task.isCompleted();
        response.createdAt = task.getCreatedAt();
        response.updatedAt = task.getUpdatedAt();
        return response;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public boolean isCompleted() {
        return completed;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }
}
