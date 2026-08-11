import { useEffect, useState } from 'react'
import { todosApi } from './api/client.js'
import AddTodo from './components/AddTodo.jsx'
import TodoList from './components/TodoList.jsx'

// App owns the single source of truth — the `todos` array. Child components are
// presentational and reach the API only through the callbacks passed down here.
export default function App() {
  const [todos, setTodos] = useState([])
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  // Load todos once, on mount.
  useEffect(() => {
    let cancelled = false
    todosApi
      .list()
      .then((data) => {
        if (!cancelled) setTodos(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  // Add todo (receives { title, priority } from AddTodo component)
  async function handleAdd({ title, priority }) {
    setError(null)
    try {
      const created = await todosApi.create({ title, priority })
      setTodos((prev) => [...prev, created])
    } catch (err) {
      setError(err.message)
      throw err // let AddTodo know NOT to clear the input
    }
  }

  // Optimistic toggle: flip the checkbox immediately, roll back if the API fails.
  async function handleToggle(id, complete) {
    setError(null)
    const previous = todos
    setTodos((prev) => prev.map((t) => (t.id === id ? { ...t, complete } : t)))
    try {
      await todosApi.toggle(id, complete)
    } catch (err) {
      setTodos(previous) // rollback
      setError(err.message)
    }
  }

  // Optimistic priority update: change priority immediately, roll back on failure.
  async function handleUpdatePriority(id, priority) {
    setError(null)
    const previous = todos
    setTodos((prev) => prev.map((t) => (t.id === id ? { ...t, priority } : t)))
    try {
      await todosApi.updatePriority(id, priority)
    } catch (err) {
      setTodos(previous) // rollback
      setError(err.message)
    }
  }

  // Optimistic delete: remove immediately, restore the list if the API fails.
  async function handleDelete(id) {
    setError(null)
    const previous = todos
    setTodos((prev) => prev.filter((t) => t.id !== id))
    try {
      await todosApi.remove(id)
    } catch (err) {
      setTodos(previous) // rollback
      setError(err.message)
    }
  }

  return (
    <main className="app">
      <h1>Todos</h1>

      <AddTodo onAdd={handleAdd} />

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      {loading ? (
        <p className="muted">Loading…</p>
      ) : (
        <TodoList
          todos={todos}
          onToggle={handleToggle}
          onDelete={handleDelete}
          onUpdatePriority={handleUpdatePriority}
        />
      )}
    </main>
  )
}