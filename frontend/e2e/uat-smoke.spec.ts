import { expect, test } from '@playwright/test'

test('UAT smoke flow: sign in, upload, and open analytics', async ({ page }) => {
  await page.goto('/signin')

  await page.locator('label:has-text("Username") input').fill('admin')
  await page.locator('label:has-text("Password") input').fill('admin123')
  await page.getByRole('button', { name: 'Sign in' }).click()

  await expect(page).toHaveURL(/\/$/)

  await page.getByRole('button', { name: 'Upload Data' }).first().click()
  await expect(page).toHaveURL(/\/upload$/)

  await page.setInputFiles('input[type="file"]', 'public/sample-data/portfolio-upload-sample.csv')
  await page.getByRole('button', { name: 'Upload to backend' }).click()

  await expect(page.getByText('Upload completed successfully.')).toBeVisible({ timeout: 20_000 })
  await expect(page.locator('.upload-result-card h3').first()).toHaveText(/success/i)

  await page.getByRole('link', { name: 'Back to dashboard' }).click()
  await expect(page).toHaveURL(/\/$/)

  await page.getByRole('button', { name: 'Open Analytics' }).first().click()
  await expect(page).toHaveURL(/\/analytics$/)
  await expect(page.getByRole('heading', { name: 'Portfolio Intelligence' })).toBeVisible()
})
