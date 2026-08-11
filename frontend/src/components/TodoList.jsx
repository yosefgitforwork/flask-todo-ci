import TodoItem from './TodoItem.jsx'

// Presentational list. Renders an empty state when there are no todos.
export default function TodoList({ todos, onToggle, onDelete, onUpdatePriority }) {
  if (todos.length === 0) {
    return (
      <p className="muted empty">Nothing here yet. Add your first todo above.</p>
    )
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
          onUpdatePriority={onUpdatePriority}
        />
      ))}
    </ul>
  )
}