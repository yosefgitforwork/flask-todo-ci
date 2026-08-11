// A single row: checkbox (toggle) + title + priority selector + delete button.
// Purely driven by props; it calls back up to App to mutate the shared state.
export default function TodoItem({ todo, onToggle, onDelete, onUpdatePriority }) {
  return (
    <li className={`todo-item ${todo.complete ? 'is-complete' : ''} priority-${todo.priority}`}>
      <label className="todo-main">
        <input
          type="checkbox"
          checked={todo.complete}
          onChange={() => onToggle(todo.id, !todo.complete)}
        />
        <span className="todo-title">{todo.title}</span>
      </label>

      {/* Priority Dropdown */}
      <select
        value={todo.priority || 'medium'}
        onChange={(e) => onUpdatePriority(todo.id, e.target.value)}
        className={`priority-select priority-${todo.priority || 'medium'}`}
        aria-label={`Priority for ${todo.title}`}
      >
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>

      <button
        type="button"
        className="delete"
        onClick={() => onDelete(todo.id)}
        aria-label={`Delete ${todo.title}`}
      >
        ×
      </button>
    </li>
  )
}