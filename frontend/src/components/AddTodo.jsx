import { useState } from 'react'

// Controlled input. Ignores empty/whitespace titles and clears itself only
// after onAdd resolves successfully (App re-throws on failure).
export default function AddTodo({ onAdd }) {
  const [title, setTitle] = useState('')
  const [priority, setPriority] = useState('medium')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) return // ignore empty / whitespace-only titles

    setSubmitting(true)
    try {
      // Pass both title and priority as an object to onAdd
      await onAdd({ title: trimmed, priority })
      setTitle('') // clear title only on success
      setPriority('medium') // reset priority back to default
    } catch {
      // App already surfaced the error; keep the text so the user can retry.
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="add-todo" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="What needs doing?"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        aria-label="New todo title"
      />

      <select
        value={priority}
        onChange={(e) => setPriority(e.target.value)}
        aria-label="Todo priority"
        className="priority-select"
        disabled={submitting}
      >
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>

      <button type="submit" disabled={submitting || !title.trim()}>
        Add
      </button>
    </form>
  )
}