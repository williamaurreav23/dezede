import React from 'react';
import PropTypes from 'prop-types';
import {computed} from "mobx";
import {observer} from "mobx-react";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";
import {withStyles} from "@material-ui/core/styles";
import GetAppIcon from '@material-ui/icons/GetApp';
import LaunchIcon from '@material-ui/icons/Launch';

import Reader from "./Reader";
import Source from "./models/Source";
import AuteurLabelList from "./labels/AuteurLabelList";
import {withTranslation} from "react-i18next";


const styles = theme => ({
  transcription: {
    fontFamily: theme.typography.fontFamilySerif,
    // Makes sure tables in the transcription have enough space between cells.
    '& table td+td': {
      paddingLeft: theme.spacing(1),
    },
  },
  transcriptionFooter: {
    marginTop: theme.spacing(1),
  },
});


@withStyles(styles)
@withTranslation('source')
@observer
class SourceView extends React.Component {
  static propTypes = {
    id: PropTypes.number.isRequired,
  };

  @computed
  get source() {
    return Source.getById(this.props.id);
  }

  get downloadButton() {
    if (!this.source.telechargement_autorise) {
      return null;
    }
    const {t} = this.props;
    let url = this.source.url;
    let icon;
    let label;
    if (url) {
      icon = <LaunchIcon fontSize="small" />;
      label = t('source:originalOn', {url: new URL(url).hostname});
    } else if (this.source.isOther) {
      url = this.source.fichier;
      icon = <GetAppIcon fontSize="small" />;
      label = `${t('source:download')} (${this.source.taille_fichier})`;
    } else {
      return null;
    }
    return (
      <Grid item>
        <Typography align="center">
          <Button component="a" target="_blank" href={url} startIcon={icon}
                  color="primary" variant="outlined" size="small">
            {label}
          </Button>
        </Typography>
      </Grid>
    );
  }

  get transcription() {
    const {classes} = this.props;
    if (!this.source.transcription) {
      return null;
    }
    return (
      <Grid item>
        <blockquote>
          <div
            dangerouslySetInnerHTML={{__html: this.source.transcription}}
            className={classes.transcription}
          />
          {
            this.source.auteurs.length > 0
              ? (
                <footer className={classes.transcriptionFooter}>
                  <AuteurLabelList ids={this.source.auteurs} />
                </footer>
              )
              : null
          }
        </blockquote>
      </Grid>
    );
  }

  get reader() {
    if (!this.source.has_images) {
      return null;
    }
    return (
      <Grid item>
        <Reader sourceId={this.props.id} />
      </Grid>
    );
  }

  render() {
    return (
      <Grid container direction="column" wrap="nowrap" spacing={4}>
        {this.downloadButton}
        {this.reader}
        {this.transcription}
      </Grid>
    );
  }
}


export default SourceView;
