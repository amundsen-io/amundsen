import axios from 'axios';

import * as API from '../v0';
import { NotificationType } from 'interfaces';

jest.mock('axios');

describe('sendNotification', () => {
  it('calls axios with the correct params', async () => {
    const testRecipients = ['user1@test.com'];
    const testSender = 'user2@test.com';
    const testNotificationType = NotificationType.OWNER_ADDED;
    const testOptions = {
      resource_name: 'testResource',
      resource_path: '/testResource',
      description_requested: false,
      fields_requested: false,
    };
    API.sendNotification(
      testRecipients,
      testSender,
      testNotificationType,
      testOptions,
    )
    expect(axios).toHaveBeenCalledWith({
      data: {
        notificationType: testNotificationType,
        options: testOptions,
        recipients: testRecipients,
        sender: testSender,
      },
      method: 'post',
      url: `/api/mail/v0/notification`,
    });

  });
});
