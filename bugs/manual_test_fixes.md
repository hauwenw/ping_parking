# Bug and Feature Request Analysis

This document outlines the design and execution plan for the bugs and missing features identified during manual testing.

---

## 1. Unique Space Names

**Analysis:** The system currently allows the creation of spaces with duplicate names within the same site, which can lead to confusion and data integrity issues. The space name should be unique per site.

**Implementation Progress & Design Decisions:**

*   **Backend (FastAPI):**
    1.  **Database Layer (Done):** Implemented a unique composite constraint on the `spaces` table for the `(site_id, name)` columns.
        *   **Decision:** Added `__table_args__ = (UniqueConstraint("site_id", "name", name="uq_spaces_site_id_name"),)` directly to the `Space` model (`backend/app/models/space.py`). This allows SQLAlchemy's `Base.metadata.create_all` (used in test setup) to pick up the constraint automatically.
        *   **Decision:** Generated a new Alembic migration script (`1b7ea1249a8b_add_unique_constraint_to_space_name_and_.py`) that correctly includes `op.create_unique_constraint` and `op.drop_constraint`.
    2.  **Service Layer (Done):** Modified `SpaceService.create` method (`backend/app/services/space_service.py`) to catch `sqlalchemy.exc.IntegrityError`.
        *   **Decision:** If `IntegrityError` is due to the unique constraint violation on `spaces.site_id, spaces.name`, it now raises a `fastapi.HTTPException` with `status.HTTP_409_CONFLICT` and the Chinese detail message "此場地已存在同名車位". This ensures a proper API response for client-side handling.
        *   **Debugging:** Initially used `BusinessError` which defaulted to 400; corrected to `HTTPException(status_code=status.HTTP_409_CONFLICT)`.
    3.  **Testing (Done):**
        *   Added `test_create_duplicate_space` to `backend/tests/test_spaces.py` to assert the `409 Conflict` behavior with the specific error message.
        *   **Debugging `passlib/bcrypt`:** Encountered `ValueError: password cannot be longer than 72 bytes`. Resolved by downgrading `bcrypt` to `3.2.0` (compatible with `passlib==1.7.4` specified in `requirements.txt`) and updating test fixture passwords to "Pass123" in `backend/tests/conftest.py` and `backend/tests/test_auth.py`.

*   **Frontend (Next.js):**
    1.  **Testing Setup (Done):** Configured Jest for unit/integration tests.
        *   **Decision:** Installed `jest`, `@testing-library/react`, `@testing-library/jest-dom`, `ts-jest`, `jest-environment-jsdom`, `@types/jest`.
        *   **Decision:** Added `test` and `test:watch` scripts to `frontend/package.json`.
        *   **Decision:** Created `frontend/jest.config.js` with `ts-jest` preset, `jsdom` environment, and `moduleNameMapper`.
        *   **Decision:** Created `frontend/jest.setup.ts` to import `@testing-library/jest-dom` and mock `Element.prototype.scrollIntoView` to address JSDOM compatibility for Radix UI components.
    2.  **Failing Test (Done):** Created `frontend/src/app/(dashboard)/spaces/page.test.tsx`.
        *   Simulates opening the space creation dialog, selecting a site, entering a duplicate space name, and submitting the form.
        *   Mocks `api.post` to `mockRejectedValueOnce` with an `ApiError` instance containing the expected 409 status and error message.
        *   **Debugging:** Initial test failures due to `TestingLibraryElementError: Found multiple elements with the text: Site A` and `Unable to find role="option" and name "Site A"` were resolved by using `screen.findByRole('button', { name: '新增車位' })` and `screen.findByRole('option', { name: 'Site A' })` to ensure elements are present and correctly targeted after asynchronous rendering. Also switched from `fireEvent.mouseDown` to `fireEvent.click` for `SelectTrigger`.
        *   **Debugging `ApiError` Mocking:** The `instanceof ApiError` check in `page.tsx` was initially failing due to a mismatch between the mocked `ApiError` in `jest.mock('@/lib/api')` and the actual `ApiError` class.
        *   **Decision:** Removed `jest.mock('@/lib/api')` and instead used `jest.spyOn(api, 'post')` on the actual `api` client. The `mockRejectedValueOnce` now throws an instance of the *actual* `ApiError` class (`new ApiError('message', 'code', status)`). This ensures the `instanceof` check passes.
    3.  **Error Handling & Display (Done):** Modified `frontend/src/app/(dashboard)/spaces/page.tsx`'s `handleSubmit` function.
        *   **Decision:** The existing `catch (err)` block with `if (err instanceof ApiError) toast.error(err.message);` is sufficient, as the backend now correctly returns a 409 with the appropriate message in `err.message`. The test now passes, confirming `toast.error` is called with "此場地已存在同名車位".

**Next Steps:** Proceed with **Item 2: Batch Space Creation and Sequential Naming**. Currently, backend tests for this feature are failing with `405 Method Not Allowed`, indicating the endpoint is not yet implemented.

---

## 2. Batch Space Creation and Sequential Naming

**Analysis:** There is currently no batch space creation workflow. The user wants to add a feature to create multiple spaces at once with sequential naming (e.g., A-01, A-02, A-03).

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **New API Endpoint:** Create a new API endpoint, e.g., `POST /api/v1/spaces/batch`, which accepts a batch configuration.
    2.  **New Pydantic Schema:** Define a schema `SpaceBatchCreateRequest` that accepts:
        *   `site_id: int`
        *   `prefix: str`
        *   `count: int` (number of spaces to create)
        *   `start_number: int = 1` (starting sequential number, e.g., for 'A-01')
        *   `tags: Optional[List[int]] = None` (list of tag IDs to apply to all spaces in the batch)
        *   `custom_price: Optional[float] = None` (optional custom price for all spaces in the batch)
    3.  **Service Layer:**
        *   Implement a new method `SpaceService.batch_create_spaces(db: Session, batch_data: SpaceBatchCreateRequest, current_user: AdminUser) -> List[Space]`.
        *   This method will first validate `site_id` exists and is accessible.
        *   It will generate space names using the provided `prefix` and sequential numbers, padding with leading zeros (e.g., `f"{prefix}-{i:02d}"`).
        *   **Pre-check for Duplicates:** Before attempting any creation, query the database to check if *any* of the generated names already exist within the specified `site_id`. If duplicates are found, raise an `HTTPException` with `409 Conflict` and a list of conflicting names.
        *   **Transaction:** Wrap the creation of all spaces in a single database transaction to ensure atomicity (all or nothing).
        *   For each new space, call the existing `SpaceService.create_space` logic (or a modified internal version) to reuse validation and business rules.
        *   **Audit Logging:** Log a single 'BATCH_CREATE_SPACES' action in `system_logs`, detailing the `site_id`, `prefix`, `count`, and the `id`s of the newly created spaces.

*   **Frontend (Next.js):**
    1.  **UI Entry Point:** Add a "Batch Create Spaces" button on the Space Management page (e.g., near the existing "Create Space" button).
    2.  **Modal Form:** Clicking the button will open a modal form with the following inputs:
        *   Site (Dropdown/Select)
        *   Prefix (Text input)
        *   Number of Spaces (Number input)
        *   Starting Number (Number input, default to 1)
        *   Tags (Multi-select dropdown, fetching available tags)
        *   Custom Price (Optional number input)
    3.  **API Integration:** On form submission, send a `POST` request to `/api/v1/spaces/batch` with the form data.
    4.  **User Feedback:**
        *   Display a loading indicator during the API call.
        *   On success, show a toast notification (e.g., "Successfully created X spaces") and close the modal. Refresh the space list.
        *   On error, display a clear, user-friendly error message in Chinese within the modal (e.g., if duplicate names were found, list them).

---

## 3. Display Tag Colors in Space List

**Analysis:** The space list page shows tags as plain text. The system was designed to have color-coded tags for better visual scanning, but this is not implemented on the list page. The `tags` table has a `color` column.

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **Verify API Response:** Ensure the `GET /api/v1/spaces` endpoint returns the full tag object (including `id`, `name`, and `color`) for each space, not just the tag name. The Pydantic schema for the space response model should be configured for this.

*   **Frontend (Next.js):**
    1.  **Locate Component:** Identify the component responsible for rendering the spaces table (likely in `src/app/(dashboard)/spaces/components/space-table.tsx`).
    2.  **Update Tag Rendering:** In the table cell that renders tags, map over the `space.tags` array.
    3.  **Apply Color:** For each tag, use a `Badge` component (from shadcn/ui). Apply the tag's color using an inline style: `style={{ backgroundColor: tag.color }}`. Ensure the text color has sufficient contrast (e.g., by setting it to black or white based on the background color's brightness).

---

## 4. Workflow to Add/Remove Tags from a Space

**Analysis:** A core piece of functionality is missing: the ability to change the tags associated with an existing space. This should be possible from the space detail page.

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **New API Endpoint:** Create `PUT /api/v1/spaces/{space_id}/tags`.
    2.  **Pydantic Schema:** Define `SpaceTagsUpdate` schema with a single field: `tag_ids: List[int]`.
    3.  **Service Logic:**
        *   Implement `SpaceService.update_space_tags`.
        *   This service will fetch the space by `space_id`.
        *   It will replace the existing list of tags on the space with the new list provided. Since tags are a PG array, this is a simple update to the column.
        *   Log the change (old tags vs. new tags) in the `system_logs` table via the `AuditLogger`.

*   **Frontend (Next.js):**
    1.  **Location:** On the space detail page (`/spaces/[id]`).
    2.  **UI Component:** Add a section for "Tags". Use a multi-select combobox component (e.g., from shadcn/ui) that allows searching and selecting from all available tags.
    3.  **State Management:** The component should be populated with the space's current tags.
    4.  **Interaction:** When the user modifies the tags and clicks a "Save" or "Update" button, call the new `PUT /api/v1/spaces/{space_id}/tags` endpoint with the updated list of tag IDs.
    5.  **Feedback:** Show a confirmation toast on success.

---

## 5. Workflow to Manually Edit a Space's Price

**Analysis:** The pricing model specifies that an admin can override the site or tag-based price with a custom price for a specific space. The UI for this is missing.

**Execution Plan:**

*   **Backend (FastAPI):**
    1.  **Verify Model/Schema:** The `Space` model should have a `custom_price: Optional[Decimal]` field. Ensure this is reflected in the Pydantic schemas.
    2.  **New API Endpoint:** Create `PUT /api/v1/spaces/{space_id}/price`.
    3.  **Pydantic Schema:** Define a schema `SpacePriceUpdate` that accepts `{ custom_price: Optional[float] }`.
    4.  **Service Logic:**
        *   Implement `SpaceService.update_space_price`.
        *   This service updates the `custom_price` field for the specified space. Setting it to `null` should revert the space to using the tag or site-based price.
        *   Log the price change in `system_logs`.

*   **Frontend (Next.js):**
    1.  **Location:** On the space detail page (`/spaces/[id]`).
    2.  **UI Component:** In an "Edit Space" form or a dedicated "Pricing" card, add an input field for "Custom Price".
    3.  **Display Logic:**
        *   Clearly label the input.
        *   Display the *effective* current price and indicate its source (e.g., "Site Default: NT$3600", "Tag Price: NT$3800", or "Custom Price: NT$3750").
        *   The input should show the current `custom_price` if set.
    4.  **Interaction:** When an admin enters a value and saves, call the `PUT /api/v1/spaces/{space_id}/price` endpoint. A button to "Clear Override" could set the price back to `null`.
    5.  **Feedback:** Show a confirmation toast and update the displayed effective price.
