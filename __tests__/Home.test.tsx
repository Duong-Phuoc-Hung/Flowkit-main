import { render, screen } from '@testing-library/react'
import Home from '../src/app/page'

describe('Home Page', () => {
  it('renders the Dashboard header', () => {
    render(<Home />)
    const header = screen.getByText(/Trạm 1: Sáng Tác Kịch Bản/i)
    expect(header).toBeInTheDocument()
  })
})
