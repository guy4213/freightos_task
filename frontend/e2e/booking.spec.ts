import { test, expect } from '@playwright/test'

test.describe('Flight Booking Flow', () => {

  test('should display list of flights', async ({ page }) => {
    await page.goto('http://localhost:5173')
    await expect(page.getByText('FR1001')).toBeVisible()
    // Use first() to avoid strict mode violation
    await expect(page.getByText('TLV').first()).toBeVisible()
  })

  test('should navigate to seat map on flight click', async ({ page }) => {
    await page.goto('http://localhost:5173')
    await page.getByText('FR1001').click()
    await expect(page).toHaveURL(/\/flights\/.*\/seats/)
    await expect(page.getByText('Select Your Seats')).toBeVisible()
  })

  test('should select seats and show live summary', async ({ page }) => {
    await page.goto('http://localhost:5173')
    await page.getByText('FR1001').click()

    await page.getByRole('button', { name: '1A' }).click()

    await expect(page.getByText('1 / 9 seats selected')).toBeVisible()
    // Check subtotal in the summary sidebar specifically
    await expect(page.locator('.summary-total')).toContainText('$200')
  })

  test('full booking flow — select seat, fill form, confirm', async ({ page }) => {
    await page.goto('http://localhost:5173')

    await page.getByText('FR1003').click()
    await expect(page).toHaveURL(/\/flights\/.*\/seats/)

    await page.getByRole('button', { name: '5B' }).click()
    await page.getByText('Continue to Checkout').click()

    await expect(page).toHaveURL('/checkout')

    // Fill passenger form
    await page.getByPlaceholder('John Doe').fill('E2E Test User')
    // Target date input directly by type
    await page.locator('input[type="date"]').fill('1990-06-15')
    await page.getByPlaceholder('+972501234567').fill('0521111111')

    await page.getByText('Confirm Booking').click()

    await expect(page).toHaveURL('/reservations')
    await expect(page.getByRole('heading', { name: 'My Reservations' })).toBeVisible()
  })

  test('should show reserved seat as disabled after booking', async ({ page }) => {
    // Book seat 6C on FR1004
    await page.goto('http://localhost:5173')
    await page.getByText('FR1004').click()
    await page.getByRole('button', { name: '6C' }).click()
    await page.getByText('Continue to Checkout').click()

    await page.getByPlaceholder('John Doe').fill('Reserved Test')
    await page.locator('input[type="date"]').fill('1985-01-01')
    await page.getByPlaceholder('+972501234567').fill('0522222222')
    await page.getByText('Confirm Booking').click()
    await expect(page).toHaveURL('/reservations')

    // Go back to same flight — seat 6C should now be disabled
    await page.goto('http://localhost:5173')
    await page.getByText('FR1004').click()
    await expect(page.getByRole('button', { name: '6C' })).toBeDisabled()
  })

  test('should cancel a booking', async ({ page }) => {
    await page.goto('http://localhost:5173/reservations')

    const cancelBtn = page.getByText('Cancel').first()
    if (await cancelBtn.isVisible()) {
      page.on('dialog', dialog => dialog.accept())
      await cancelBtn.click()
      await expect(page.getByText('cancelled').first()).toBeVisible()
    }
  })

})