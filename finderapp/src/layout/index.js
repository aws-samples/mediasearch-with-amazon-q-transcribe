import React from 'react';
import { AppLayout } from '@cloudscape-design/components';
import { I18nProvider } from '@cloudscape-design/components/i18n';
import messages from '@cloudscape-design/components/i18n/messages/all.en';

import './style.css';

import Sidenavigation from './sidenavigation';
import Tools from './tools';

const LOCALE = 'en';

export default function Layout({
  children,
  breadcrumbs,
  navigationOpenFlag = false,
  toolsOpenFlag = false,
  notifications = null
}) {
  return (
    <I18nProvider locale={LOCALE} messages={[messages]}>
      <AppLayout
        breadcrumbs={breadcrumbs}
        navigationOpen={navigationOpenFlag}
        onNavigationChange={({ detail }) => {}}
        onToolsChange={({ detail }) => {}}
        navigationHide={true}
        toolsHide={true}
        navigation={<Sidenavigation />}
        notifications={notifications}
        toolsOpen={toolsOpenFlag}
        tools={<Tools />}
        content={children}
      />
    </I18nProvider>
  );
}