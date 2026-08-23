import { useState } from 'react';
import {
  Button,
  IconButton,
  Panel,
  PanelHeader,
  Badge,
  StatusBadge,
  Metric,
  DataRow,
  Tabs,
  Modal,
  Drawer,
  Tooltip,
  ProgressBar,
  Skeleton,
} from '../components/ui';
import { EmptyState } from '../components/feedback/EmptyState';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { Bell, Download, Plus, Search } from 'lucide-react';

export const DesignSystemPage: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="p-6 space-y-8 overflow-y-auto h-full bg-[var(--color-marine-navy-dark)]">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">MarineShield Design System</h1>
        <p className="text-sm text-slate-500">Component reference for the maritime intelligence command center.</p>
      </div>

      {/* Buttons */}
      <Section title="Buttons">
        <div className="flex flex-wrap gap-2 items-center">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
          <Button variant="primary" disabled>Disabled</Button>
        </div>
        <div className="flex flex-wrap gap-2 items-center mt-3">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </div>
      </Section>

      {/* Icon Buttons */}
      <Section title="Icon Buttons">
        <div className="flex gap-2 items-center">
          <IconButton label="Bell"><Bell /></IconButton>
          <IconButton label="Download"><Download /></IconButton>
          <IconButton label="Add"><Plus /></IconButton>
          <IconButton label="Search"><Search /></IconButton>
        </div>
      </Section>

      {/* Badges */}
      <Section title="Badges">
        <div className="flex flex-wrap gap-2 items-center">
          <Badge>Default</Badge>
          <Badge variant="info">Info</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="danger">Danger</Badge>
          <Badge variant="cyan">Cyan</Badge>
        </div>
      </Section>

      {/* Status Badges */}
      <Section title="Status Badges">
        <div className="flex flex-wrap gap-4 items-center">
          <StatusBadge status="online" />
          <StatusBadge status="offline" />
          <StatusBadge status="warning" />
          <StatusBadge status="danger" />
          <StatusBadge status="unknown" />
        </div>
      </Section>

      {/* Panel & PanelHeader */}
      <Section title="Panel">
        <Panel>
          <PanelHeader title="Incident Summary">
            <Badge variant="warning">Pending</Badge>
          </PanelHeader>
          <p className="text-xs text-slate-400">Panel content area for displaying structured intelligence data.</p>
        </Panel>
      </Section>

      {/* Metric */}
      <Section title="Metric">
        <div className="flex gap-6">
          <Metric label="Label A" value="—" unit="units" />
          <Metric label="Label B" value="—" />
          <Metric label="Label C" value="—" unit="km²" />
        </div>
      </Section>

      {/* DataRow */}
      <Section title="DataRow">
        <Panel>
          <DataRow label="Detection Method" value="SAR Analysis" />
          <DataRow label="Confidence" value="—" />
          <DataRow label="Status" value="Awaiting data" />
        </Panel>
      </Section>

      {/* Tabs */}
      <Section title="Tabs">
        <Panel>
          <Tabs
            tabs={[
              { id: 'overview', label: 'Overview', content: <p className="text-xs text-slate-400">Overview content area.</p> },
              { id: 'evidence', label: 'Evidence', content: <p className="text-xs text-slate-400">Evidence content area.</p> },
              { id: 'history', label: 'History', content: <p className="text-xs text-slate-400">History content area.</p> },
            ]}
          />
        </Panel>
      </Section>

      {/* Tooltip */}
      <Section title="Tooltip">
        <div className="flex gap-4">
          <Tooltip content="Top tooltip"><Button variant="secondary">Hover me (top)</Button></Tooltip>
          <Tooltip content="Bottom tooltip" side="bottom"><Button variant="secondary">Hover me (bottom)</Button></Tooltip>
        </div>
      </Section>

      {/* ProgressBar */}
      <Section title="ProgressBar">
        <div className="space-y-3 max-w-sm">
          <ProgressBar value={25} />
          <ProgressBar value={50} variant="success" />
          <ProgressBar value={75} variant="warning" />
          <ProgressBar value={90} variant="danger" />
        </div>
      </Section>

      {/* Skeleton */}
      <Section title="Skeleton">
        <div className="max-w-sm">
          <Skeleton lines={4} />
        </div>
      </Section>

      {/* Feedback States */}
      <Section title="Feedback States">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Panel className="h-48 flex items-center justify-center">
            <LoadingState message="Loading intelligence…" />
          </Panel>
          <Panel className="h-48 flex items-center justify-center">
            <EmptyState title="No incidents" message="No incidents currently match your filter criteria." />
          </Panel>
          <Panel className="h-48 flex items-center justify-center">
            <ErrorState title="Connection Error" message="Unable to reach the intelligence service." />
          </Panel>
        </div>
      </Section>

      {/* Modal */}
      <Section title="Modal">
        <Button variant="secondary" onClick={() => setModalOpen(true)}>Open Modal</Button>
        <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Confirm Action">
          <p className="text-sm text-slate-400 mb-4">Modal content goes here.</p>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={() => setModalOpen(false)}>Confirm</Button>
          </div>
        </Modal>
      </Section>

      {/* Drawer */}
      <Section title="Drawer">
        <Button variant="secondary" onClick={() => setDrawerOpen(true)}>Open Drawer</Button>
        <Drawer open={drawerOpen} onClose={() => setDrawerOpen(false)} title="Detail Panel">
          <p className="text-sm text-slate-400">Drawer content area for detailed intelligence inspection.</p>
        </Drawer>
      </Section>
    </div>
  );
};

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section>
    <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3 border-b border-slate-800/50 pb-2">
      {title}
    </h2>
    {children}
  </section>
);
