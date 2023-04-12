// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import { API_PATH } from 'ducks/tableMetadata/api/v0';
import { ResourceType } from 'interfaces/Resources';
import { UpdateMethod } from 'interfaces/Enums';

import * as OwnerUtils from './owner';

describe('owner', () => {
  describe('createOwnerUpdatePayload', () => {
    it('creates the right update payload', () => {
      const testId = 'testId@test.com';
      const testKey = 'testKey';
      const testMethod = UpdateMethod.PUT;

      expect(
        OwnerUtils.createOwnerUpdatePayload(ResourceType.table, testKey, {
          method: testMethod,
          id: testId,
        })
      ).toMatchObject({
        method: testMethod,
        url: `${API_PATH}/update_table_owner`,
        data: {
          key: testKey,
          owner: testId,
        },
      });
    });
  });

  describe('getOwnersDictFromUsers ', () => {
    it('correctly reformats users into the owners dict', () => {
      const mockUsers = [
        {
          display_name: 'test',
          profile_url: 'test.io',
          email: 'test@test.com',
          user_id: 'test',
        },
      ];

      expect(OwnerUtils.getOwnersDictFromUsers(mockUsers)).toEqual({
        test: {
          display_name: 'test',
          profile_url: 'test.io',
          email: 'test@test.com',
          user_id: 'test',
        },
      });
    });
  });

  describe('createOwnerUpdatePayload ', () => {
    it('correctly reformats users into the owners dict', () => {
      const mockResourceType = ResourceType.table;
      const mockKey = 'testKey';
      const mockPayload = {
        id: 'testId',
        method: UpdateMethod.PUT,
      };

      expect(
        OwnerUtils.createOwnerUpdatePayload(
          mockResourceType,
          mockKey,
          mockPayload
        )
      ).toEqual({
        url: `${API_PATH}/update_table_owner`,
        method: mockPayload.method,
        data: {
          key: mockKey,
          owner: mockPayload.id,
        },
      });
    });

    describe('when URL is defined', () => {
      it('throws an error', () => {
        const mockResourceType = ResourceType.user;
        const mockKey = 'testKey';
        const mockPayload = {
          id: 'testId',
          method: UpdateMethod.PUT,
        };

        expect(() => {
          OwnerUtils.createOwnerUpdatePayload(
            mockResourceType,
            mockKey,
            mockPayload
          );
        }).toThrow();
      });
    });
  });
});
