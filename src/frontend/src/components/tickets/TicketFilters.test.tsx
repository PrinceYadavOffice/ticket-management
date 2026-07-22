import { describe, expect, it } from 'vitest';

import { filtersToApiParams } from './TicketFilters';

describe('filtersToApiParams', () => {
  it('maps form state to API filter params', () => {
    const params = filtersToApiParams(
      {
        q: 'printer',
        status: 'Open',
        priority: 'High',
        assignedTo: '2',
        unassigned: false,
      },
      1,
      20,
    );
    expect(params).toEqual({
      q: 'printer',
      status: 'Open',
      priority: 'High',
      assignedTo: 2,
      page: 1,
      pageSize: 20,
    });
  });
});
